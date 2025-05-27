import streamlit as st
import requests

# Load API key securely from Streamlit Secrets
API_KEY = st.secrets["TOGETHER_API_KEY"]

# API and headers setup
API_URL = "https://api.together.xyz/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Streamlit app UI
st.set_page_config(page_title="Chatbot with Together.ai", layout="centered")
st.title("🤖 Chatbot (Together.ai)")

# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# User input
user_input = st.text_input("You:", placeholder="Ask me anything...")

# Call Together.ai API
def get_response(message, history):
    payload = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",  # Free & powerful
        "messages": history + [{"role": "user", "content": message}],
        "temperature": 0.7,
        "max_tokens": 300
    }

    response = requests.post(API_URL, headers=HEADERS, json=payload)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Error: {response.status_code} - {response.text}"

# Handle input and display chat
if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    reply = get_response(user_input, st.session_state.chat_history)
    st.session_state.chat_history.append({"role": "assistant", "content": reply})

# Show conversation history
for msg in st.session_state.chat_history:
    role = "You" if msg["role"] == "user" else "Bot"
    st.markdown(f"**{role}:** {msg['content']}")
