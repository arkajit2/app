import streamlit as st
from transformers import pipeline, set_seed

st.set_page_config(page_title="Fraoula LLM Chatbot", page_icon="🤖")

st.title(" Fraoula Local LLM Chatbot")

# Initialize the text generation pipeline once, cached for performance
@st.cache_resource
def load_generator():
    set_seed(42)
    return pipeline('text-generation', model='distilgpt2')

generator = load_generator()

# Initialize chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def generate_response(prompt):
    # Generate text continuation from the model
    output = generator(prompt, max_length=100, num_return_sequences=1)
    # Extract generated text (skip the prompt part)
    generated_text = output[0]['generated_text'][len(prompt):].strip()
    return generated_text

# User input
user_input = st.text_input("You:", placeholder="Type your message here...")

if user_input:
    # Add user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    # Prepare context for the model by concatenating previous conversation (last 3 exchanges max)
    context = ""
    # We'll keep max 3 previous messages (user + bot) for context
    for chat in st.session_state.chat_history[-6:]:
        role = "User" if chat["role"] == "user" else "Bot"
        context += f"{role}: {chat['content']}\n"
    context += "Bot: "
    
    # Generate bot response
    bot_response = generate_response(context)
    
    # Add bot response to chat history
    st.session_state.chat_history.append({"role": "bot", "content": bot_response})
    
# Display chat history
for chat in st.session_state.chat_history:
    if chat["role"] == "user":
        st.markdown(f"**You:** {chat['content']}")
    else:
        st.markdown(f"**Bot:** {chat['content']}")
