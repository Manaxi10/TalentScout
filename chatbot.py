from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
import os
from pymongo import MongoClient
import json
from dotenv import load_dotenv

load_dotenv()

class TalentScoutChatbot:
    def __init__(self):
        """Initialize the TalentScout Hiring Assistant chatbot."""
        self.llm = ChatGroq(
            model_name="llama3-70b-8192",
            temperature=0.7,
            api_key=os.getenv("GROQ_API_KEY")
        )
        mongo_uri = os.getenv("MONGO_CONNECTION_STRING")
        # mongo_uri = "mongodb+srv://user:user@cluster0.24wqbyj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        self.mongo_client = MongoClient(mongo_uri)
        self.db = self.mongo_client.Talentscout
        self.userinfo_col = self.db["userinfo"]
        self.messages_col = self.db["messages"]

    def load_chat_history(self):
        """Load previous chat history from MongoDB."""
        try:
            # Get all messages sorted by insertion order
            messages = list(self.messages_col.find().sort([('_id', 1)]))
            
            # Convert MongoDB documents to the format expected by Streamlit
            chat_history = []
            for msg in messages:
                chat_history.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            return chat_history
        except Exception as e:
            print(f"Error loading chat history: {e}")
            return []

    def clear_chat_history(self):
        """Clear all chat history from MongoDB."""
        try:
            self.messages_col.delete_many({})
            self.userinfo_col.delete_many({})
            print("Chat history cleared successfully")
        except Exception as e:
            print(f"Error clearing chat history: {e}")

    def get_response(self, user_input):
        """Process user input and generate a response."""
        last_msgs = list(self.messages_col.find().sort([('_id', -1)]).limit(20))
        # Reverse to chronological order
        last_msgs = last_msgs[::-1]
        
        last_msg = ""
        
        for i in last_msgs:
            last_msg = i['content']

        # Format as conversation history
        conversation_history = ""
        for msg in last_msgs:
            conversation_history += f"{msg['role'].capitalize()}: {msg['content']}\n"
        
        fields = [
            "name", "email", "phone", "experience", "desired_position", "current_location", "languages", "frameworks", "databases", "tools"
        ]
        
        user_info = ""
        collected_fields = []
        
        # Check which fields are already collected
        for i in fields:
            result = self.userinfo_col.find_one({"fieldname": i})
            if result != None:
                collected_fields.append(i)
                if i == "languages" or i == "frameworks" or i == "databases" or i == "tools":
                    user_info += f'\n{i} : {result[i]}'
                else:
                    user_info += f'\n{i} : {result[i]}'
        
        # Check if all required fields are collected
        all_fields_collected = len(collected_fields) == len(fields)
        
        # Only extract information if not all fields are collected
        if not all_fields_collected:
            prompt1 = """
            You are a bot and supposed to extract information from the user message.
            Only extract the information don't respond anything to the user.
            You will be given a user message and you need to extract any of the the following information:
            - name (string)
            - email (string)
            - phone (string)
            - experience (string)
            - desired_position (string)
            - current_location (string)
            - languages (string)
            - frameworks (string)
            - databases (string)
            - tools (string)
            
            And return the response as formatted JSON.
            If information is not provided don't assume them as a blank just don't add them in json response
            Example response:
                Example 1 - 
                [{
                    'languages': "Python, JavaScript",
                    'frameworks': "Django, React",
                    'databases': "PostgreSQL, MongoDB",
                    'tools': "Docker, Kubernetes"

                }]
                Example 2 - 
                [{  
                    "name": "Jane Smith",
                ]}
                Example 3 -
                [{
                    "name": "John Doe",
                    "email": "john.doe@example.com"
                    "phone": "123-456-7890",
                    "experience": "5 years in software development",
                    "desired_position": "Software Engineer",
                    "current_location": "San Francisco, CA" 
                }]
                
            Don't give any preamble text in reponse.
            If no information is user message, return an empty JSON array.
            Example response:
                [{}]
                
            Last question asked to the user was:
            {last_msg}
            """
            
            system_message1 = SystemMessage(content=prompt1)
            
            # Get LLM response for information extraction
            response1 = self.llm.invoke([system_message1, HumanMessage(content=user_input)])
            
            user_data = {}

            if '[{' in response1.content:
                print('----------------------')
                user_data = response1.content.strip().split('[')[-1].split(']')[0]
                print("User data - "+user_data)
                
                try:
                    user_data = json.loads(user_data)
                except json.JSONDecodeError:
                    user_data = {}
        
            if len(list(user_data.keys())) != 0:
                fieldname = list(user_data.keys())[0]
                user_data['fieldname'] = fieldname

                print("User Data Extracted:", user_data)
                
                filter_query = {'fieldname': fieldname}
                update_data = {"$set": user_data}
                
                self.userinfo_col.update_one(filter_query, update_data, upsert=True)
        else:
            print("All required fields are already collected. Skipping information extraction.")

        prompt2 = f"""
        You are the TalentScout Hiring Assistant, designed to help with interacting with candidates for tech positions.
        
        Collect the information from the user and ask relevant technical questions based on the information provided.
        
        Don't answer any questions from user. And start from where you left before user asked question.
        
        For starters, please gather the following information:
        - Name
        - Email 
        - Phone Number
        - Experience
        - Desired Position
        - Current Location
        - Programming Languages
        - Frameworks
        - Databases
        - Tools
        
        User Information:
        {user_info}

        Check all of the 10 inforation is present in user information section ,if not ask the user for that information.
        
        Collect the information one by one, and after each response, ask the next question.
        
        Ask one question at a time while collecting the missing information, and wait for the user's response before proceeding to the next question.
        
        Unless the previous question is answered don't move to next question.
        
        Based on the declared tech stack, ask relevant technical questions to assess the candidate's skills.
        
        Ask 3-5 technical questions on each of topic which include programming language -> frameworks -> databases -> tools known by user in these order.

        Once the 3-5 tools related technical questions are answered, Gracefully conclude the conversation, thanking the candidate and informing them recruiter from our side will analyze your profile and answers and get back to you soon.

        Last 20 messages in the conversation:
        {conversation_history}
        """
        
        system_message2 = SystemMessage(content=prompt2)
        
        user_input_msg = HumanMessage(content=user_input)
        
        # Get LLM response for conversation
        response2 = self.llm.invoke([system_message2, user_input_msg])
        
        # Store messages in database
        self.messages_col.insert_one({
            'role': 'user',
            'content': user_input
        })
        
        self.messages_col.insert_one({
            'role': 'assistant',
            'content': response2.content
        })

        return response2.content
    
    def get_collected_user_info(self):
        """Get all collected user information from MongoDB."""
        try:
            fields = [
                "name", "email", "phone", "experience", "desired_position", 
                "current_location", "languages", "frameworks", "databases", "tools"
            ]
            
            collected_info = {}
            
            for field in fields:
                result = self.userinfo_col.find_one({"fieldname": field})
                if result and field in result:
                    collected_info[field] = result[field]
            
            return collected_info
        except Exception as e:
            print(f"Error getting collected user info: {e}")
            return {}
