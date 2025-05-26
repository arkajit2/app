import os
import streamlit as st
from huggingface_hub import hf_hub_download
from llama_cpp import Llama

# ------------------ Config ------------------
REPO_ID = "Arkajit1/Bloke"
MODEL_FILENAME = "capybarahermes-2.5-mistral-7b.Q8_0.gguf"
MODEL_PATH = os.path.join("models", MODEL_FILENAME)

# ------------------ Streamlit UI ------------------
st.set_page_config(page_title="Fraoula LLaMA Chatbot", page_icon="🤖")
st.title("🤖 Fraoula Local Chatbot — Mistral 7B (Capybara Hermes 2.5)")

# ------------------ Model Download ------------------
@st.cache_resource
def download_model():
    os.makedirs("models", exist_ok=True)
    if not os.path.exists(MODEL_PATH):
        st.info("Downloading GGUF model from Hugging Face...")
        hf_hub_download(repo_id=REPO_ID, filename=MODEL_FILENAME, local_dir="models", local_dir_use_symlinks=False)
    return MODEL_PATH

# ------------------ Load Model ------------------
@st.cache_resource
def load_llm():
    model_path = download_model()
    return Llama(
        model_path=model_path,
        n_ctx=2048,
        n_threads=8,  # Adjust based on your CPU
        temperature=0.7,
        top_p=0.9,
        stop=["User:", "Bot:"]
    )

llm = load_llm()

# ------------------ Chat Memory ------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ------------------ Chat Logic ------------------
def generate_response(prompt):
    output = llm(prompt, max_tokens=512)
    return output["choices"][0]["text"].strip()

# ------------------ UI Input ------------------
user_input = st.text_input("You:", placeholder="Type your message here...")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # Create prompt from recent history
    context = ""
    for chat in st.session_state.chat_history[-6:]:
        role = "User" if chat["role"] == "user" else "Bot"
        context += f"{role}: {chat['content']}\n"
    context += "Bot:"

    bot_reply = generate_response(context)
    st.session_state.chat_history.append({"role": "bot", "content": bot_reply})

# ------------------ Chat Display ------------------
for chat in st.session_state.chat_history:
    speaker = "**You:**" if chat["role"] == "user" else "**Bot:**"
    st.markdown(f"{speaker} {chat['content']}")
