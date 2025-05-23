import streamlit as st
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

st.set_page_config(page_title="Fraoula Chatbot", page_icon="🤖")
st.title("🤖 Fraoula Chatbot with DialoGPT")

@st.cache_resource(show_spinner=False)
def load_model():
    tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
    model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-small")
    return tokenizer, model

tokenizer, model = load_model()

# Initialize chat history in session state
if "chat_history_ids" not in st.session_state:
    st.session_state.chat_history_ids = None
if "step" not in st.session_state:
    st.session_state.step = 0

def generate_response(user_input):
    # Encode user input and add end of string token
    new_input_ids = tokenizer.encode(user_input + tokenizer.eos_token, return_tensors='pt')

    # Append new user input tokens to chat history (if exists)
    if st.session_state.chat_history_ids is not None:
        bot_input_ids = torch.cat([st.session_state.chat_history_ids, new_input_ids], dim=-1)
    else:
        bot_input_ids = new_input_ids

    # Generate response with model
    chat_history_ids = model.generate(
        bot_input_ids,
        max_length=1000,
        pad_token_id=tokenizer.eos_token_id,
        no_repeat_ngram_size=3,
        do_sample=True,
        top_k=50,
        top_p=0.95,
        temperature=0.75,
    )

    # Update chat history
    st.session_state.chat_history_ids = chat_history_ids

    # Decode bot response
    response = tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
    return response

# Streamlit UI

user_input = st.text_input("You:", key="input_text", placeholder="Type your message here and press Enter")

if user_input:
    response = generate_response(user_input)
    st.session_state.step += 1

    # Display chat messages
    if "messages" not in st.session_state:
        st.session_state.messages = []

    st.session_state.messages.append({"user": user_input, "bot": response})

# Display chat history
if "messages" in st.session_state:
    for chat in st.session_state.messages:
        st.markdown(f"**You:** {chat['user']}")
        st.markdown(f"**Bot:** {chat['bot']}")

