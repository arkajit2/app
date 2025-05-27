import streamlit as st
import requests
import json # Import json for parsing the response

# --- Gemini API Configuration ---
# In a real Streamlit deployment, you would load this from Streamlit Secrets.
# For local testing, you can uncomment and set it directly, but remember to secure it.
# API_KEY = "YOUR_GEMINI_API_KEY_HERE"

# IMPORTANT: For Canvas environment, the API key is automatically provided
# by the platform. You should leave API_KEY as an empty string or
# use the __api_key global variable if available, as shown below.
# However, for Streamlit, st.secrets is the correct way to handle it.
# So, we'll assume st.secrets["GEMINI_API_KEY"] is used for deployment.

# Load API key securely from Streamlit Secrets
# Make sure you have a secret named "GEMINI_API_KEY" in your Streamlit app's secrets.toml
# Example secrets.toml:
# [secrets]
# GEMINI_API_KEY="YOUR_ACTUAL_GEMINI_API_KEY"
API_KEY = st.secrets["GEMINI_API_KEY"]

# Gemini API endpoint for text generation (gemini-2.0-flash model)
# We are using gemini-2.0-flash as it's a good balance of performance and cost.
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

HEADERS = {
    "Content-Type": "application/json",
    # The API key is passed as a query parameter for Gemini's generateContent endpoint
    # and also can be passed in the URL directly, as shown in the fetch call in the instructions.
    # For requests.post, it's often included in the URL or as a header.
    # We will include it in the URL for consistency with the provided instructions.
}

# --- Streamlit App UI ---
st.set_page_config(page_title="Chatbot with Gemini API", layout="centered")
st.title("🤖 Chatbot (Gemini API)")

# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# User input
user_input = st.text_input("You:", placeholder="Ask me anything...")

# Function to call Gemini API
def get_gemini_response(message, history):
    # Gemini API expects messages in a specific format:
    # [{"role": "user", "parts": [{"text": "..."}]}, {"role": "model", "parts": [{"text": "..."}]}]
    
    # Convert existing chat history to Gemini format
    gemini_history = []
    for msg in history:
        role = "user" if msg["role"] == "user" else "model"
        gemini_history.append({"role": role, "parts": [{"text": msg["content"]}]})

    # Add the current user message
    gemini_history.append({"role": "user", "parts": [{"text": message}]})

    payload = {
        "contents": gemini_history,
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 300, # Max tokens for the response
        }
    }

    # Construct the URL with the API key as a query parameter
    full_api_url = f"{API_URL}?key={API_KEY}"

    try:
        response = requests.post(full_api_url, headers=HEADERS, json=payload)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        
        # Parse the JSON response
        response_data = response.json()

        # Extract the content from the response
        if response_data and response_data.get("candidates"):
            # The response structure for generateContent is:
            # { "candidates": [ { "content": { "parts": [ { "text": "..." } ] } } ] }
            return response_data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return f"Error: Unexpected response structure - {response_data}"

    except requests.exceptions.RequestException as e:
        return f"Error connecting to Gemini API: {e}"
    except json.JSONDecodeError as e:
        return f"Error decoding JSON response: {e} - Response: {response.text}"
    except KeyError as e:
        return f"Error parsing Gemini response (missing key): {e} - Response: {response.text}"


# Handle input and display chat
if user_input:
    # Add user message to history
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # Get response from Gemini
    with st.spinner("Thinking..."): # Show a spinner while waiting for the response
        reply = get_gemini_response(user_input, st.session_state.chat_history)
    
    # Add bot response to history
    st.session_state.chat_history.append({"role": "assistant", "content": reply})

# Show conversation history
for msg in st.session_state.chat_history:
    role = "You" if msg["role"] == "user" else "Bot"
    st.markdown(f"**{role}:** {msg['content']}")

