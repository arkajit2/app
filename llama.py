import streamlit as st
import requests
import json

# --- OpenRouter API Configuration ---
API_KEY = "YOUR_API_KEY_HERE"  # Replace with your OpenRouter API key
API_URL = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# --- Custom Color Theme (Fraoula Violet) ---
PRIMARY_COLOR = "#9400D3"  # Deep Violet
SECONDARY_COLOR = "#C779D9"  # Light Violet
BACKGROUND_COLOR = "#1E003E"  # Dark violet background
TEXT_COLOR = "#FFFFFF"  # White text

# --- Streamlit App Styling ---
st.set_page_config(page_title="Chatbot with OpenRouter Llama API", layout="wide")

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

            # Prepare messages for OpenRouter API
            # OpenRouter expects a list of messages with roles 'user' and 'assistant'
            def get_openrouter_response(messages):
                payload = {
                    "model": "meta-llama/llama-4-pythia",  # Example model, change as needed
                    "messages": messages,
                    "max_tokens": 300,
                    "temperature": 0.7,
                }
                try:
                    response = requests.post(API_URL, headers=HEADERS, json=payload)
                    response.raise_for_status()
                    data = response.json()
                    # Extract reply text
                    return data["choices"][0]["message"]["content"]
                except requests.exceptions.RequestException as e:
                    return f"API Request Error: {e}"
                except KeyError:
                    return f"Unexpected API response structure: {data}"

            # Convert session chat to OpenRouter message format
            openrouter_messages = []
            for msg in st.session_state.chat_history:
                role = "user" if msg["role"] == "user" else "assistant"
                openrouter_messages.append({"role": role, "content": msg["content"]})

            with st.spinner("Thinking..."):
                bot_reply = get_openrouter_response(openrouter_messages)

            # Append bot reply after API call
            st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
