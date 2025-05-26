import streamlit as st
from llama_cpp import Llama

# ---- Configuration ----
MODEL_PATH = "llama-3-8b-instruct.Q4_K_M.gguf"  # Make sure this file is present in the directory

# ---- Streamlit UI ----
st.set_page_config(page_title="Fraoula LLaMA 3 Chatbot", page_icon="🤖")
st.title("🤖 Fraoula Local LLaMA 3 Chatbot")

# ---- Load LLaMA model (cached) ----
@st.cache_resource
def load_llama_model():
    return Llama(
        model_path=MODEL_PATH,
        n_ctx=2048,
        n_threads=8,       # adjust based on your CPU
        temperature=0.7,
        top_p=0.95,
        stop=["User:", "Bot:"]
    )

llm = load_llama_model()

# ---- Session State for Chat ----
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---- Function to Generate Response ----
def generate_response(prompt):
    output = llm(prompt, max_tokens=256)
    return output["choices"][0]["text"].strip()

# ---- Input from User ----
user_input = st.text_input("You:", placeholder="Type your message and hit Enter")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # Build prompt context from last 3 exchanges
    context = ""
    for msg in st.session_state.chat_history[-6:]:
        role = "User" if msg["role"] == "user" else "Bot"
        context += f"{role}: {msg['content']}\n"
    context += "Bot:"

    # Generate and store bot reply
    bot_reply = generate_response(context)
    st.session_state.chat_history.append({"role": "bot", "content": bot_reply})

# ---- Display Chat ----
for msg in st.session_state.chat_history:
    role = "**You:**" if msg["role"] == "user" else "**Bot:**"
    st.markdown(f"{role} {msg['content']}")
