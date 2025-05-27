import streamlit as st
import requests
import json

# --- Gemini API Configuration ---
API_KEY = st.secrets["GEMINI_API_KEY"]
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
HEADERS = {"Content-Type": "application/json"}

# --- Dark Violet Theme Colors ---
PRIMARY_COLOR = "#6A0DAD"        # Rich Deep Violet
SECONDARY_COLOR = "#9B59B6"      # Soft Violet Accent
BACKGROUND_COLOR = "#1A0033"     # Very Dark Violet / Near Black
TEXT_COLOR = "#FFFFFF"           # Pure White for strong contrast
INPUT_BG_COLOR = "#2E004F"       # Dark Violet input background
BORDER_COLOR = "#7D4B9E"         # Violet border for inputs/buttons
BOT_BG_COLOR = "#3B0070"         # Darker violet for bot messages
USER_BG_COLOR = "#7B3FBF"        # Slightly lighter violet for user messages

# --- Streamlit App Styling ---
st.set_page_config(page_title="Chatbot with Gemini API", layout="wide", page_icon="🤖")

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {BACKGROUND_COLOR};
        color: {TEXT_COLOR};
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}

    .stTextInput > div > div > input {{
        background-color: {INPUT_BG_COLOR} !important;
        color: {TEXT_COLOR} !important;
        border: 2px solid {BORDER_COLOR} !important;
        border-radius: 12px !important;
        padding: 12px !important;
        font-size: 16px !important;
        transition: border-color 0.3s ease;
    }}
    .stTextInput > div > div > input:focus {{
        border-color: {PRIMARY_COLOR} !important;
        outline: none !important;
        box-shadow: 0 0 8px {PRIMARY_COLOR};
    }}

    .stButton > button {{
        background-color: {PRIMARY_COLOR} !important;
        color: {TEXT_COLOR} !important;
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-weight: 600;
        font-size: 16px;
        border: none;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }}
    .stButton > button:hover {{
        background-color: {SECONDARY_COLOR} !important;
    }}

    .user-message {{
        background-color: {USER_BG_COLOR};
        color: {TEXT_COLOR};
        padding: 14px 20px;
        border-radius: 20px 20px 0 20px;
        margin: 6px 0 6px 30%;
        max-width: 70%;
        font-size: 16px;
        line-height: 1.4;
        box-shadow: 0 2px 6px rgba(0,0,0,0.5);
        text-align: right;
        word-wrap: break-word;
    }}
    .bot-message {{
        background-color: {BOT_BG_COLOR};
        color: {TEXT_COLOR};
        padding: 14px 20px;
        border-radius: 20px 20px 20px 0;
        margin: 6px 30% 6px 0;
        max-width: 70%;
        font-size: 16px;
        line-height: 1.4;
        box-shadow: 0 2px 6px rgba(0,0,0,0.5);
        text-align: left;
        word-wrap: break-word;
    }}

    .chat-container {{
        max-height: 70vh;
        overflow-y: auto;
        padding-right: 10px;
        scrollbar-width: thin;
        scrollbar-color: {PRIMARY_COLOR} transparent;
    }}
    .chat-container::-webkit-scrollbar {{
        width: 8px;
    }}
    .chat-container::-webkit-scrollbar-thumb {{
        background-color: {PRIMARY_COLOR};
        border-radius: 10px;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def get_gemini_response(message, history):
    gemini_history = []
    for msg in history:
        role = "user" if msg["role"] == "user" else "model"
        gemini_history.append({"role": role, "parts": [{"text": msg["content"]}]})

    gemini_history.append({"role": "user", "parts": [{"text": message}]})

    payload = {
        "contents": gemini_history,
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 300,
        },
    }

    full_api_url = f"{API_URL}?key={API_KEY}"

    try:
        response = requests.post(full_api_url, headers=HEADERS, json=payload)
        response.raise_for_status()
        response_data = response.json()
        if response_data and response_data.get("candidates"):
            return response_data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return f"Error: Unexpected response structure - {response_data}"

    except requests.exceptions.RequestException as e:
        return f"Error connecting to Gemini API: {e}"
    except json.JSONDecodeError as e:
        return f"Error decoding JSON response: {e} - Response: {response.text}"
    except KeyError as e:
        return f"Error parsing Gemini response (missing key): {e} - Response: {response.text}"

# --- INPUT FORM first ---
with st.form(key="input_form", clear_on_submit=True):
    user_input = st.text_input("You:", placeholder="Type your message...")
    submit = st.form_submit_button("Send")

    if submit and user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.spinner("Thinking..."):
            reply = get_gemini_response(user_input, st.session_state.chat_history)
        st.session_state.chat_history.append({"role": "assistant", "content": reply})

# --- THEN DISPLAY CHAT HISTORY BELOW FORM ---
chat_container = st.container()
with chat_container:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f'<div class="user-message">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-message">{msg["content"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
