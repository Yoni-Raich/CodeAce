import streamlit as st
import os
import json
from datetime import datetime
from codeace import MappingAgent, CoreAgent

# Constants
ASSISTANT_AVATAR_PATH = 'https://imgur.com/FgmmmH7.png'
USER_AVATAR_PATH = 'https://ps.w.org/user-avatar-reloaded/assets/icon-128x128.png'

# Page config
st.set_page_config(layout="wide", page_title="Code Ace™", page_icon="🤖")

# Custom CSS
st.markdown(
    """
    <style>
    .main {
        max-width: 80%;
        margin: 0 auto;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'current_source' not in st.session_state:
    st.session_state.current_source = None
if 'mapping_done' not in st.session_state:
    st.session_state.mapping_done = False
if 'core_agent' not in st.session_state:
    st.session_state.core_agent = None

def save_conversation(messages, filename):
    """Save conversation history to a file"""
    history_folder = os.path.join(os.path.dirname(__file__), "history")
    os.makedirs(history_folder, exist_ok=True)
    file_path = os.path.join(history_folder, filename)
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(messages, file, ensure_ascii=False, indent=2)
    return file_path

def load_conversation(file_path):
    """Load conversation history from a file"""
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def process_user_query(messages):
    """Process the latest user query"""
    if not st.session_state.core_agent:
        return "Please select a source directory and run the mapping process first."
    
    user_input = messages[-1]["content"]
    
    with st.spinner('Finding relevant files...'):
        relevant_files = st.session_state.core_agent.find_relevant_files(user_input)
        st.write(f"📁 Found relevant files: {'\n'.join(relevant_files)}\n\n")
        
    with st.spinner('Generating response...'):
        response = st.session_state.core_agent.process_code_query(user_input, relevant_files)
        return response

def run_mapping_process(src_path):
    """Run the mapping process for the selected source"""
    with st.spinner('Running mapping process...'):
        mapping_agent = MappingAgent(model_name="azure", src_path=src_path)
        mapping_agent.run_mapping_process()
        st.session_state.core_agent = CoreAgent(model_name="azure", src_path=src_path)
        st.session_state.mapping_done = True
        return True

st.title("Code Ace™")

# Sidebar
with st.sidebar:
    st.image('https://imgur.com/EQE1jjg.png', width=100)
    
    # Source directory input
    src_path = st.text_input("Source Directory Path")
    if src_path:
        st.session_state.current_source = src_path
        if st.button("Run Mapping Process"):
            if run_mapping_process(src_path):
                st.success("Mapping completed!")
    
    # New chat button
    if st.button("New Chat"):
        st.session_state.messages = []
    
    # Save conversation
    if st.button("Save Conversation"):
        if st.session_state.messages:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"chat_history_{timestamp}.json"
            saved_path = save_conversation(st.session_state.messages, filename)
            st.success(f"Conversation saved to {saved_path}")
        else:
            st.warning("No conversation to save.")
    
    # Load conversation
    uploaded_file = st.file_uploader("Load Conversation", type="json")
    if uploaded_file is not None:
        loaded_messages = json.loads(uploaded_file.getvalue())
        st.session_state.messages = loaded_messages
        st.success("Conversation loaded successfully!")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=ASSISTANT_AVATAR_PATH if message["role"] == "assistant" else USER_AVATAR_PATH):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What would you like to know about the code?"):
    if not st.session_state.mapping_done:
        st.error("Please run the mapping process first.")
    else:
        # Display user message
        st.chat_message("user", avatar=USER_AVATAR_PATH).markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Get and display assistant response
        response = process_user_query(st.session_state.messages)
        with st.chat_message("assistant", avatar=ASSISTANT_AVATAR_PATH):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})