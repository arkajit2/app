import streamlit as st
import requests
import json

# --- Gemini API Configuration ---
API_KEY = st.secrets["GEMINI_API_KEY"]
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
HEADERS = {"Content-Type": "application/json"}

# --- Dark Violet Theme Colors ---
PRIMARY_COLOR = "#6A0DAD"        # Deep Violet
SECONDARY_COLOR = "#9B59B6"      # Lighter Violet Accent
BACKGROUND_COLOR = "#1A0033"     # Dark Violet almost black
TEXT_COLOR = "#FFFFFF"           # White text
INPUT_BG_COLOR = "#2E004F"       # Dark violet input background
BORDER_COLOR = "#7D4B9E"         # Violet border
BOT_BG_COLOR = "#3B0070"         # Bot message bubble
USER_BG_COLOR = "#7B3FBF"        # User message bubble

# --- Page Config ---
st.set_page_config(page_title="Chatbot with Gemini API", layout="wide", page_icon="🤖")

# --- CSS Styling ---
st.markdown(f"""
<style>
    /* App background and font */
    .stApp {{
        background-color: {BACKGROUND_COLOR};
        color: {TEXT_COLOR};
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        height: 100vh;
        display: flex;
        flex-direction: column;
    }}

    /* Chat container: flex-grow to fill, scrollable */
    #chat-container {{
        flex-grow: 1;
        overflow-y: auto;
        padding: 1rem 2rem;
        display: flex;
        flex-direction: column;
        gap: 12px;
        scroll-behavior: smooth;
        max-height: 75vh;
    }}

    /* User message bubble (right aligned) */
    .user-message {{
        align-self: flex-end;
        background-color: {USER_BG_COLOR};
        color: {TEXT_COLOR};
        padding: 14px 22px;
        border-radius: 20px 20px 0 20px;
        max-width: 70%;
        font-size: 16px;
        line-height: 1.4;
        box-shadow: 0 2px 6px rgba(0,0,0,0.6);
        white-space: pre-wrap;
        word-wrap: break-word;
    }}

    /* Bot message bubble (left aligned) */
    .bot-message {{
        align-self: flex-start;
        background-color: {BOT_BG_COLOR};
        color: {TEXT_COLOR};
        padding: 14px 22px;
        border-radius: 20px 20px 20px 0;
        max-width: 70%;
        font-size: 16px;
        line-height: 1.4;
        box-shadow: 0 2px 6px rgba(0,0,0,0.6);
        white-space: pre-wrap;
        word-wrap: break-word;
    }}

    /* Input container fixed below chat */
    #input-container {{
        padding: 10px 2rem;
        background-color: {BACKGROUND_COLOR};
        border-top: 1px solid {BORDER_COLOR};
        display: flex;
        gap: 10px;
        align-items: center;
    }}

    /* Text input style */
    #user-input {{
        flex-grow: 1;
        background-color: {INPUT_BG_COLOR} !important;
        color: {TEXT_COLOR} !important;
        border: 2px solid {BORDER_COLOR} !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
        font-size: 16px !important;
        outline: none !important;
        transition: border-color 0.3s ease;
    }}

    #user-input:focus {{
        border-color: {PRIMARY_COLOR} !important;
        box-shadow: 0 0 8px {PRIMARY_COLOR};
    }}

    /* Send button style */
    #send-button {{
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

    #send-button:hover {{
        background-color: {SECONDARY_COLOR} !important;
    }}

    /* Scrollbar styling */
    #chat-container::-webkit-scrollbar {{
        width: 8px;
    }}
    #chat-container::-webkit-scrollbar-thumb {{
        background-color: {PRIMARY_COLOR};
        border-radius: 10px;
    }}
</style>
""", unsafe_allow_html=True)


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


# --- Main layout ---
# Use a form to enable Enter key submission and clearing input after send
with st.form(key="chat_form", clear_on_submit=True):
    # Chat display container
    chat_container = st.container()
    
    # Input and button fixed below chat
    col1, col2 = st.columns([8, 1])
    with col1:
        user_input = st.text_input("You:", key="user-input", placeholder="Type your message here...", label_visibility="collapsed")
    with col2:
        send_button = st.form_submit_button("Send", help="Press Enter to send")

    # Display chat messages below input (outside the form)
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f'<div class="user-message">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="bot-message">{msg["content"]}</div>', unsafe_allow_html=True)

    # Process input on submit
    if send_button and user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.spinner("Thinking..."):
            reply = get_gemini_response(user_input, st.session_state.chat_history)
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        # Scroll to bottom will happen naturally on rerun

# Scroll chat to bottom on every rerun using JS hack
scroll_script = """
<script>
const chatContainer = window.parent.document.querySelector('#chat-container div[role="list"]') || window.parent.document.querySelector('#chat-container');
if(chatContainer) {
  chatContainer.scrollTop = chatContainer.scrollHeight;
}
</script>
"""
st.markdown(scroll_script, unsafe_allow_html=True)
