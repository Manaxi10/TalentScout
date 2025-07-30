# TalentScout Hiring Assistant

A intelligent AI-powered chatbot designed to assist in the initial screening of candidates for technology positions at TalentScout recruitment agency.

## Project Overview

The TalentScout Hiring Assistant is an AI-powered chatbot that:

- Gathers essential candidate information (name, contact details, experience, etc.)
- Understands candidates' tech stacks
- Generates relevant technical questions based on declared technologies
- Provides a seamless interview experience with persistent chat history
- Maintains conversation context and ensures a coherent flow
- Stores all data in MongoDB for persistence across sessions

## Features

- **Intelligent Information Extraction**: Uses LLM to extract structured data from natural conversations
- **Persistent Chat History**: All conversations are stored in MongoDB and persist across sessions
- **Real-time Progress Tracking**: Sidebar shows collection progress and candidate information
- **Technical Assessment**: Generates relevant technical questions based on candidate's tech stack
- **Professional UI**: Clean, modern interface with custom styling
- **Session Management**: Ability to reset conversations and start fresh

## Installation Instructions

### Prerequisites

- Python 3.8 or higher
- Groq API key
- MongoDB Atlas account (or local MongoDB instance)

### Setup

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd TalentScout
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - MacOS/Linux: `source venv/bin/activate`

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Create a `.env` file in the project root and add your API keys:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   MONGO_CONNECTION_STRING=your_mongodb_connection_string_here
   ```

### Running the Application

```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501` in your web browser.

## Usage Guide

1. Open the application in your web browser
2. The chatbot will greet you and start asking for your information
3. Answer the questions truthfully and concisely
4. When asked about your tech stack, list all technologies, programming languages, frameworks, and tools you are proficient in
5. Answer the technical questions to the best of your ability
6. The chatbot will summarize the collected information at the end of the conversation
7. Type "exit", "quit", or "bye" at any time to end the conversation
8. Use the "Reset Chat" button in the sidebar to start a new conversation

## Technical Details

### Libraries Used

- **Streamlit**: Frontend UI framework for the web interface
- **LangChain**: Framework for working with language models
- **Groq**: Provider of the underlying language model (Llama 3-70B)
- **PyMongo**: MongoDB driver for Python
- **python-dotenv**: For environment variable management
- **dnspython**: Required for MongoDB Atlas connections

### Architecture

The application follows a modular architecture:

1. **Frontend ([app.py](app.py))**: Streamlit-based user interface
   - Custom CSS styling for professional appearance
   - Real-time chat interface
   - Sidebar with candidate information and progress tracking
   - Session state management

2. **Chatbot Logic ([chatbot.py](chatbot.py))**: Core chatbot functionality
   - [`TalentScoutChatbot`](chatbot.py) class handles all chatbot operations
   - Information extraction using LLM
   - MongoDB integration for data persistence
   - Conversation flow management

3. **Database Integration**: MongoDB for persistent storage
   - `userinfo` collection: Stores extracted candidate information
   - `messages` collection: Stores complete chat history

### Conversation Flow

The conversation follows a structured flow:
1. **Greeting**: Welcome message and introduction
2. **Personal Information**: Name, email, phone number
3. **Professional Details**: Experience, desired position, location
4. **Technical Skills**: Programming languages, frameworks, databases, tools
5. **Technical Assessment**: 3-5 questions per technology category
6. **Conclusion**: Summary and next steps

## Prompt Engineering

### Information Extraction Prompt
The system uses a specialized prompt to extract structured information from user responses:
- Focuses on specific fields (name, email, phone, etc.)
- Returns data in JSON format
- Handles missing information gracefully

### Conversation Management Prompt
The main conversation prompt:
- Maintains professional tone
- Ensures one question at a time
- Tracks conversation progress
- Generates relevant technical questions based on tech stack

## Configuration

### Environment Variables
- `GROQ_API_KEY`: Your Groq API key for accessing Llama 3 model
- `MONGO_CONNECTION_STRING`: MongoDB connection string for data persistence

### Model Configuration
- **Model**: `llama3-70b-8192`
- **Temperature**: 0.7 (balanced creativity and consistency)
- **Provider**: Groq (for fast inference)

## File Structure

```
├── app.py                 # Main Streamlit application
├── chatbot.py            # Core chatbot logic and MongoDB integration
├── requirements.txt      # Python dependencies
├── .env                 # Environment variables (not in repo)
├── README.md            # This documentation
└── dockerfile           # Docker configuration (if needed)
```
