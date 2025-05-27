import streamlit as st
import requests
import json

# --- Gemini API Configuration ---
API_KEY = st.secrets["GEMINI_API_KEY"]
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
HEADERS = {"Content-Type": "application/json"}

# Initialize chat history
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

# --- Streamlit UI ---
st.set_page_config(page_title="Gemini Chat", layout="wide")

# (Insert your CSS styling here — omitted for brevity but use the last style I gave you)

# --- Chat display container ---
chat_container = st.container()

with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("You:", placeholder="Type your message here...", key="input_text", label_visibility="collapsed")
    submitted = st.form_submit_button("Send")

    if submitted and user_input.strip():
        # Append user message immediately
        st.session_state.chat_history.append({"role": "user", "content": user_input.strip()})

        # Call API and append bot reply immediately
        with st.spinner("Thinking..."):
            bot_reply = get_gemini_response(user_input.strip(), st.session_state.chat_history)
        st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})

# Render chat history below input
with chat_container:
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f'<div class="user-message">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-message">{msg["content"]}</div>', unsafe_allow_html=True)
