import streamlit as st
import requests
import json

# --- Gemini API Configuration ---
API_KEY = st.secrets["GEMINI_API_KEY"]
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
HEADERS = {"Content-Type": "application/json"}

# --- Custom Color Theme (Dark Violet) ---
PRIMARY_COLOR = "#4B0082"       # Indigo / Dark Violet
SECONDARY_COLOR = "#7B1FA2"     # Medium Violet
BACKGROUND_COLOR = "#1E003E"    # Very Dark Violet (Background)
TEXT_COLOR = "#EDE7F6"          # Light Violet / White-ish text

st.set_page_config(page_title="Chatbot with Gemini API", layout="wide")

# Apply custom CSS styles for dark violet theme and chat bubbles
st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {BACKGROUND_COLOR};
        color: {TEXT_COLOR};
        font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    }}
    /* Input box */
    .stTextInput > div > div > input {{
        background-color: #3A0070;
        border: 2px solid {PRIMARY_COLOR};
        border-radius: 10px;
        color: {TEXT_COLOR};
        padding: 12px;
        font-size: 16px;
    }}
    /* Button */
    .stButton > button {{
        background-color: {PRIMARY_COLOR};
        color: white;
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 16px;
        transition: background-color 0.3s ease;
    }}
    .stButton > button:hover {{
        background-color: {SECONDARY_COLOR};
        cursor: pointer;
    }}
    /* User message bubble */
    .user-message {{
        background-color: {SECONDARY_COLOR};
        color: white;
        padding: 14px 18px;
        border-radius: 20px 20px 0 20px;
        margin-bottom: 10px;
        max-width: 70%;
        margin-left: auto;
        font-size: 16px;
        box-shadow: 0 3px 6px rgba(123, 31, 162, 0.5);
        word-wrap: break-word;
        white-space: pre-wrap;
    }}
    /* Bot message bubble */
    .bot-message {{
        background-color: #311B92;
        color: {TEXT_COLOR};
        padding: 14px 18px;
        border-radius: 20px 20px 20px 0;
        margin-bottom: 10px;
        max-width: 70%;
        margin-right: auto;
        font-size: 16px;
        box-shadow: 0 3px 6px rgba(75, 0, 130, 0.6);
        word-wrap: break-word;
        white-space: pre-wrap;
    }}
    /* Scrollable chat container */
    .chat-container {{
        max-height: 65vh;
        overflow-y: auto;
        padding-right: 12px;
        margin-bottom: 24px;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize chat history in session state
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

# --- Input form at the top ---
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("You:", placeholder="Type your message...")
    send_button = st.form_submit_button("Send")

if send_button and user_input.strip():
    user_message = user_input.strip()
    st.session_state.chat_history.append({"role": "user", "content": user_message})

    with st.spinner("Thinking..."):
        bot_reply = get_gemini_response(user_message, st.session_state.chat_history)

    st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})

# --- Chat messages container ---
chat_container = st.container()
with chat_container:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    # Show latest messages at top (reverse order)
    for msg in reversed(st.session_state.chat_history):
        if msg["role"] == "user":
            st.markdown(f'<div class="user-message">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-message">{msg["content"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
