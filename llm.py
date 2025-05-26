import streamlit as st
from llama_cpp import Llama

# Set Streamlit page config
st.set_page_config(page_title="Fraoula LLM Chatbot", page_icon="")
st.title(" Fraoula Local LLaMA 3 Chatbot")

# Load LLaMA model (cached)
@st.cache_resource
def load_model():
    return Llama(
        model_path="llama-3-8b-instruct.Q4_K_M.gguf",  # Replace with your model path
        n_ctx=2048,
        n_threads=8,  # Adjust based on your CPU
        temperature=0.7,
        top_p=0.95,
        stop=["User:", "Bot:"]
    )

llm = load_model()

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def generate_response(prompt):
    output = llm(prompt, max_tokens=200)
    return output["choices"][0]["text"].strip()

# User input
user_input = st.text_input("You:", placeholder="Type your message here...")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    # Prepare context (last 3 exchanges max)
    context = ""
    for chat in st.session_state.chat_history[-6:]:
        role = "User" if chat["role"] == "user" else "Bot"
        context += f"{role}: {chat['content']}\n"
    context += "Bot: "

    bot_response = generate_response(context)
    st.session_state.chat_history.append({"role": "bot", "content": bot_response})

# Display chat
for chat in st.session_state.chat_history:
    role_label = "**You:**" if chat["role"] == "user" else "**Bot:**"
    st.markdown(f"{role_label} {chat['content']}")
