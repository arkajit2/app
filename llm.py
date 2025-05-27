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
BACKGROUND_COLOR = "#1E003E"  # Dark violet background (darker for better contrast)
TEXT_COLOR = "#FFFFFF"  # White text for rich contrast

# --- Streamlit App Styling ---
st.set_page_config(page_title="Chatbot with Gemini API", layout="wide")

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {BACKGROUND_COLOR};
        color: {TEXT_COLOR};
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    .stTextInput > div > div > input {{
        background-color: #2a004f;
        border: 2px solid {PRIMARY_COLOR};
        border-radius: 8px;
        color: {TEXT_COLOR};
        padding: 10px;
    }}
    .stTextInput > div > div > input::placeholder {{
        color: #c0a8ff;
        opacity: 1;
    }}
    .stButton > button {{
        background-color: {PRIMARY_COLOR};
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        border: none;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }}
    .stButton > button:hover {{
        background-color: {SECONDARY_COLOR};
    }}
    .user-message {{
        background-color: {SECONDARY_COLOR};
        color: white;
        padding: 10px;
        border-radius: 12px 12px 0 12px;
        margin-bottom: 8px;
        text-align: right;
        max-width: 75%;
        margin-left: 25%;
        word-wrap: break-word;
        font-size: 1rem;
    }}
    .bot-message {{
        background-color: #3b0070;
        color: {TEXT_COLOR};
        padding: 10px;
        border-radius: 12px 12px 12px 0;
        margin-bottom: 8px;
        text-align: left;
        max-width: 75%;
        margin-right: 25%;
        word-wrap: break-word;
        font-size: 1rem;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Chatbot Layout ---
chat_container = st.container()
input_container = st.container()

with chat_container:
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f'<div class="user-message">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-message">{msg["content"]}</div>', unsafe_allow_html=True)

with input_container:
    # Use form for Enter key submission support
    with st.form("input_form", clear_on_submit=True):
        col1, col2 = st.columns([8, 2])  # Input and button width
        with col1:
            user_input = st.text_input("You:", placeholder="Type your message...", key="input_text")
        with col2:
            send_button = st.form_submit_button("Send")

        if send_button and user_input.strip():
            user_message = user_input.strip()

            # Append user message before API call
            st.session_state.chat_history.append({"role": "user", "content": user_message})

            # Call Gemini API function
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

            with st.spinner("Thinking..."):
                bot_reply = get_gemini_response(user_message, st.session_state.chat_history)

            # Append bot reply after API call
            st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})

            # No rerun needed — chat updates on next Streamlit rerun cycle automatically

