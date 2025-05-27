import streamlit as st
import requests
import json

# --- Gemini API Configuration ---
API_KEY = st.secrets["GEMINI_API_KEY"]
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
HEADERS = {"Content-Type": "application/json"}

# --- Custom Color Theme (Fraoula Violet) ---
PRIMARY_COLOR = "#9400D3"  # Deep Violet
SECONDARY_COLOR = "#C779D9"  # Light Violet
BACKGROUND_COLOR = "#F3E5F5"  # Very Light Violet
TEXT_COLOR = "#333333"  # Dark Gray for readability

# --- Streamlit App Styling ---
st.set_page_config(page_title="Chatbot with Gemini API", layout="wide")

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {BACKGROUND_COLOR};
        display: flex;
        flex-direction: column;
        height: 100vh;
    }}
    .chat-container {{
        flex: 1 1 auto;
        overflow-y: auto;
        padding: 10px 20px;
    }}
    .input-container {{
        flex: 0 0 auto;
        padding: 10px 20px;
        border-top: 1px solid #ccc;
        background-color: white;
    }}
    .stTextInput > div > div > input {{
        border-color: {PRIMARY_COLOR};
        border-width: 2px;
        border-radius: 8px;
        padding: 10px;
        width: 100%;
        box-sizing: border-box;
    }}
    .stButton > button {{
        background-color: {PRIMARY_COLOR};
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        width: 100%;
    }}
    .user-message {{
        background-color: {SECONDARY_COLOR};
        color: white;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 8px;
        text-align: right;
        max-width: 80%;
        margin-left: auto;
        word-wrap: break-word;
    }}
    .bot-message {{
        background-color: white;
        color: {TEXT_COLOR};
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 8px;
        text-align: left;
        border: 1px solid #ddd;
        max-width: 80%;
        margin-right: auto;
        word-wrap: break-word;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state keys
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "input_text" not in st.session_state:
    st.session_state.input_text = ""

# Container for chat messages with scrolling
chat_placeholder = st.container()

with chat_placeholder:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f'<div class="user-message">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-message">{msg["content"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Input section fixed at t
