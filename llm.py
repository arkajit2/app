import streamlit as st
import requests
import json

# --- Gemini API Configuration ---
API_KEY = st.secrets["GEMINI_API_KEY"]
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
HEADERS = {"Content-Type": "application/json"}

# --- Custom Colors ---
PRIMARY_COLOR = "#9400D3"
SECONDARY_COLOR = "#C779D9"
BACKGROUND_COLOR = "#F3E5F5"
TEXT_COLOR = "#333333"

st.set_page_config(page_title="Chatbot with Gemini API", layout="wide")

# Inject CSS for styling and layout
st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {BACKGROUND_COLOR};
        display: flex;
        flex-direction: column;
        height: 100vh;
    }}
    .chat-box {{
        flex-grow: 1;
        overflow-y: auto;
        padding: 20px;
        margin-bottom: 15px;
    }}
    .input-box {{
        border-top: 1px solid #ddd;
        padding: 10px 20px;
        background-color: white;
    }}
    .stTextInput > div > div > input {{
        border: 2px solid {PRIMARY_COLOR};
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
        margin-bottom: 10px;
        max-width: 80%;
        margin-left: auto;
        word-wrap: break-word;
        text-align: right;
    }}
    .bot-message {{
        background-color: white;
        color: {TEXT_COLOR};
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 10px;
        max-width: 80%;
        margin-right: auto;
        word-wrap: break-word;
        border: 1px solid #ddd;
        text-align: left;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "input_text" not in st.session_state:
    st.session_state.input_text = ""

# Chat messages container (scrollable)
chat_container = st.container()
with chat_container:
    st.markdown('<div class="chat-box">', unsafe_allow_html=True)
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f'<div class="user-message">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-message">{msg["content"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Input container fixed below chat
input_container = st.container()
with input_container:
    st.markdown('<div class="input-box">', unsafe_allow_html=True)
    cols = st.columns([8, 2])
    with cols[0]:
        user_input = st.text_input(
            label="",
            placeholder="Type your message...",
            key="input_text",
            label_visibility="collapsed",
            value=st.session_state.input_text,
        )
    with cols[1]:
        send_pressed = st.button("Send")
    st.markdown('</div>', unsafe_allow_html=True)

# Gemini API call function
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

# Handle sending message
if send_pressed and user_input.strip():
    st.session_state.chat_history.append({"role": "user", "content": user_input.strip()})

    with st.spinner("Thinking..."):
        bot_reply = get_gemini_response(user_input.strip(), st.session_state.chat_history)

    st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})

    # Clear input text
    st.session_state.input_text = ""

    # Rerun app to update UI
    st.experimental_rerun()
