import streamlit as st
from chatbot import TalentScoutChatbot
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="TalentScout Hiring Assistant",
    page_icon="👨‍💼",
    layout="centered"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .stTextInput>div>div>input {border-radius: 10px;}
    .main .block-container {padding-top: 2rem; padding-bottom: 2rem;}
    .stChat {border-radius: 10px;}
    .user-message {
        background-color: #d1e7dd;
        color: #155724;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        border: 1px solid #badbcc;
    }
    .assistant-message {
        background-color: #cff4fc;
        color: #055160;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        border: 1px solid #b6effb;
    }
    .chat-container {
        max-height: 500px;
        overflow-y: auto;
        padding: 10px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize chatbot first
if "chatbot" not in st.session_state:
    st.session_state.chatbot = TalentScoutChatbot()

# Initialize session state for chat history and load from MongoDB
if "messages" not in st.session_state:
    # Load previous chat history from MongoDB
    previous_messages = st.session_state.chatbot.load_chat_history()
    st.session_state.messages = previous_messages

# App header
st.title("👨‍💼 TalentScout Hiring Assistant")
st.markdown("Welcome to TalentScout's AI-powered Hiring Assistant! I'm here to help with your initial screening process.")

# Create a container for chat messages
chat_container = st.container()

# Process user input BEFORE displaying messages
user_input = st.chat_input("Type your message here...")

if user_input:
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Get chatbot response
    response = st.session_state.chatbot.get_response(user_input)
    
    # Add assistant message to history
    st.session_state.messages.append({"role": "assistant", "content": response})
    

# Display chat history in the container
with chat_container:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Display all messages
    for i, message in enumerate(st.session_state.messages):
        role = message["role"]
        content = message["content"]
        
        if role == "user":
            st.markdown(f'<div class="user-message"><strong>You:</strong> {content}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="assistant-message"><strong>Hiring Assistant:</strong> {content}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Auto-scroll to bottom using JavaScript
if st.session_state.messages:
    st.markdown("""
    <script>
        var chatContainer = document.querySelector('.chat-container');
        if (chatContainer) {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        
        // Alternative method using setTimeout to ensure DOM is ready
        setTimeout(function() {
            var containers = document.querySelectorAll('.stMarkdown');
            var lastContainer = containers[containers.length - 1];
            if (lastContainer) {
                lastContainer.scrollIntoView({ behavior: 'smooth', block: 'end' });
            }
        }, 100);
    </script>
    """, unsafe_allow_html=True)

# Display a sidebar with information about the app
with st.sidebar:
    st.title("📋 Candidate Information")
    
    # Get collected user information
    collected_info = st.session_state.chatbot.get_collected_user_info()
    
    if collected_info:
        st.markdown("### Collected Details:")
        
        # Display each field if it exists
        fields_display = {
            "name": "👤 Name",
            "email": "📧 Email", 
            "phone": "📱 Phone",
            "experience": "💼 Experience",
            "desired_position": "🎯 Desired Position",
            "current_location": "📍 Location",
            "languages": "💻 Programming Languages",
            "frameworks": "🔧 Frameworks",
            "databases": "🗃️ Databases",
            "tools": "🛠️ Tools"
        }
        
        for field, display_name in fields_display.items():
            if field in collected_info:
                value = collected_info[field]
                if value:  # Only show if value is not empty
                    st.markdown(f"**{display_name}:** {value}")
        
        # Show completion progress
        total_fields = len(fields_display)
        collected_fields = len([f for f in collected_info.values() if f])
        progress = collected_fields / total_fields if total_fields > 0 else 0
        
        st.markdown("---")
        st.markdown("### Collection Progress")
        st.progress(progress)
        st.markdown(f"**{collected_fields}/{total_fields} fields collected**")
        
    else:
        st.markdown("### 👋 Welcome!")
        st.markdown("Start the conversation to begin collecting candidate information.")
        
        st.markdown("""
        **We'll collect:**
        - 👤 Personal Details
        - 💼 Experience Level  
        - 🎯 Career Goals
        - 💻 Technical Skills
        """)
    
    st.markdown("---")
    
    # Reset chat button
    if st.button("🔄 Reset Chat"):
        st.session_state.chatbot.clear_chat_history()  # Clear from database
        st.session_state.messages = []
        st.session_state.chatbot = TalentScoutChatbot()
        st.rerun()
    
    # Show chat statistics
    st.markdown("---")
    st.markdown("### 📊 Chat Statistics")
    st.markdown(f"**Total Messages:** {len(st.session_state.messages)}")
    if st.session_state.messages:
        user_msgs = len([m for m in st.session_state.messages if m["role"] == "user"])
        assistant_msgs = len([m for m in st.session_state.messages if m["role"] == "assistant"])
        st.markdown(f"**User Messages:** {user_msgs}")
        st.markdown(f"**Assistant Messages:** {assistant_msgs}")

# Display message count at bottom for debugging
if st.session_state.messages:
    st.caption(f"Displaying {len(st.session_state.messages)} messages")
