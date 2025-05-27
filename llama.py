import streamlit as st
import requests

# --- Read OpenRouter API key securely ---
API_KEY = st.secrets["openrouter"]["api_key"]
API_URL = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# --- Theme Colors (Fraoula Violet) ---
PRIMARY_COLOR = "#9400D3"
SECONDARY_COLOR = "#C779D9"
BACKGROUND_COLOR = "#1E003E"
TEXT_COLOR = "#FFFFFF"

# --- Streamlit Setup ---
st.set_page_config(page_title="Fraoula Chatbot - OpenRouter", layout="wide")

# --- Styling ---
st.markdown(f"""
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
    .stButton > button {{
        background-color: {PRIMARY_COLOR};
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        border: none;
        cursor: pointer;
    }}
    .stButton > button:hover {{
        background-color: {SECONDARY_COLOR};
    }}
    .user-message {{
        background-color: {SECONDARY_COLOR};
        padding: 10px;
        border-radius: 12px 12px 0 12px;
        margin: 8px 0;
        text-align: right;
        max-width: 75%;
        margin-left: auto;
        color: white;
        font-size: 1rem;
    }}
    .bot-message {{
        background-color: #3b0070;
        padding: 10px;
        border-radius: 12px 12px 12px 0;
        margin: 8px 0;
        text-align: left;
        max-width: 75%;
        margin-right: auto;
        color: {TEXT_COLOR};
        font-size: 1rem;
    }}
    </style>
""", unsafe_allow_html=True)

# --- Chat History ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Display Chat ---
chat_container = st.container()
with chat_container:
    for msg in st.session_state.chat_history:
        css = "user-message" if msg["role"] == "user" else "bot-message"
        st.markdown(f'<div class="{css}">{msg["content"]}</div>', unsafe_allow_html=True)

# --- Input ---
with st.form("chat_form", clear_on_submit=True):
    col1, col2 = st.columns([8, 2])
    with col1:
        user_input = st.text_input("You:", placeholder="Ask anything...")
    with col2:
        send_btn = st.form_submit_button("Send")

    if send_btn and user_input.strip():
        user_msg = user_input.strip()
        st.session_state.chat_history.append({"role": "user", "content": user_msg})

        # Build messages
        formatted = [{"role": m["role"], "content": m["content"]} for m in st.session_state.chat_history]

        payload = {
            "model": "meta-llama/llama-3-8b-instruct",  # You can change the model here
            "messages": formatted,
            "max_tokens": 300,
            "temperature": 0.7
        }

        with st.spinner("Thinking..."):
            try:
                res = requests.post(API_URL, headers=HEADERS, json=payload)
                res.raise_for_status()
                bot_reply = res.json()["choices"][0]["message"]["content"]
            except Exception as e:
                bot_reply = f"❌ Error: {e}"

        st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
        st.rerun()  # ✅ updated to latest rerun function
