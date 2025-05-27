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
TEXT_COLOR = "#333333"      # Dark Gray for readability
BORDER_COLOR = "#E0E0E0"    # Light gray for message borders

# --- Streamlit App Styling ---
st.set_page_config(page_title="Chatbot with Gemini API", layout="wide")

# Apply custom theme and styling for a chat-like look
st.markdown(
    f"""
    <style>
    /* Overall app background */
    .stApp {{
        background-color: {BACKGROUND_COLOR};
        font-family: Arial, sans-serif;
    }}

    /* Main container for chat history - enables scrolling */
    .chat-history-container {{
        height: calc(100vh - 150px); /* Adjust height to leave space for input */
        overflow-y: auto; /* Enable vertical scrolling */
        padding: 15px;
        margin-bottom: 10px;
        background-color: white; /* Chat background */
        border-radius: 10px;
        border: 1px solid {BORDER_COLOR};
    }}

    /* User message bubble */
    .user-message {{
        background-color: {SECONDARY_COLOR};
        color: white;
        padding: 12px 15px;
        border-radius: 18px 18px 2px 18px; /* Rounded corners for chat bubble shape */
        margin-bottom: 10px;
        max-width: 75%;
        margin-left: auto; /* Pushes user message to the right */
        word-wrap: break-word; /* Ensures long words wrap */
    }}

    /* Bot message bubble */
    .bot-message {{
        background-color: white;
        color: {TEXT_COLOR};
        padding: 12px 15px;
        border-radius: 18px 18px 18px 2px; /* Rounded corners for chat bubble shape */
        margin-bottom: 10px;
        max-width: 75%;
        margin-right: auto; /* Pushes bot message to the left */
        border: 1px solid {BORDER_COLOR};
        word-wrap: break-word;
    }}

    /* Input container at the bottom */
    .fixed-input-container {{
        position: fixed; /* This attempts to fix it, but Streamlit rerenders */
        bottom: 0;
        left: 0;
        width: 100%;
        padding: 15px;
        background-color: {BACKGROUND_COLOR};
        border-top: 1px solid {BORDER_COLOR};
        box-shadow: 0 -2px 10px rgba(0,0,0,0.05); /* Subtle shadow */
        z-index: 999; /* Ensure it's on top */
    }}

    /* Streamlit's native input and button styles */
    .stTextInput > div > div > input {{
        border-color: {PRIMARY_COLOR};
        border-width: 2px;
        border-radius: 25px; /* Pill-shaped input */
        padding: 12px 20px;
        font-size: 16px;
        box-shadow: none;
    }}
    .stTextInput > div > div > input:focus {{
        box-shadow: 0 0 0 0.1rem {SECONDARY_COLOR};
        border-color: {PRIMARY_COLOR};
    }}

    .stButton > button {{
        background-color: {PRIMARY_COLOR};
        color: white;
        border-radius: 25px; /* Pill-shaped button */
        padding: 12px 20px;
        font-size: 16px;
        border: none;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }}
    .stButton > button:hover {{
        background-color: {SECONDARY_COLOR};
    }}

    /* Hide default Streamlit "You:" label for text input */
    .stTextInput label {{
        display: none;
    }}

    /* Make sure all elements fit within containers */
    .st-emotion-cache-1c7y2vl, .st-emotion-cache-k3w81l {{ /* Adjust specific Streamlit classes if needed */
        max-width: 100%;
        padding-right: 0px;
        padding-left: 0px;
    }}

    </style>
    """,
    unsafe_allow_html=True,
)

# --- Chatbot Layout ---
# Use a placeholder for chat history to enable scrolling
chat_history_placeholder = st.empty()

# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Function to call Gemini API ---
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

# --- Display Chat History ---
with chat_history_placeholder.container():
    st.title("🤖 Gemini Chatbot") # Title inside the scrollable area
    st.markdown('<div class="chat-history-container">', unsafe_allow_html=True)
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f'<div class="user-message">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-message">{msg["content"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True) # Close the chat history container div

# --- Input Area (Fixed at the bottom visually) ---
# Create an empty placeholder at the very bottom for the input
input_placeholder = st.empty()

with input_placeholder.container():
    # Use columns to align the text input and button
    col1, col2 = st.columns([0.9, 0.1]) # Adjust ratios for input and button

    with col1:
        # Use a key to clear the input after sending
        user_input = st.text_input("You:", placeholder="Send a message...", key="user_input_box")
    with col2:
        # Add some vertical space to align the button with the text input
        st.write("") # Or st.text("")
        send_button = st.button("Send")

# --- Handle Input and Get Response ---
# Check if Enter key was pressed or Send button was clicked
if send_button or user_input and st.session_state.get("last_input_sent", "") != user_input:
    # Only process if there's actual input
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.session_state["last_input_sent"] = user_input # Store the sent input to prevent duplicate processing

        with st.spinner("Thinking..."):
            reply = get_gemini_response(user_input, st.session_state.chat_history)
        st.session_state.chat_history.append({"role": "assistant", "content": reply})

        # Clear the input box by resetting its value in session state and rerunning
        st.session_state.user_input_box = ""
        st.rerun()

# --- Maintain scrolling position (requires JS, which is complex in Streamlit) ---
# For a truly persistent scroll-to-bottom, you'd need custom JavaScript,
# which is beyond simple Streamlit Python. Streamlit reruns make this tricky.
# However, the chat-history-container with overflow-y: auto will allow manual scrolling.
