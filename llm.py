import os
import streamlit as st
from huggingface_hub import hf_hub_download
from llama_cpp import Llama

REPO_ID = "Arkajit1/Bloke"
MODEL_FILENAME = "capybarahermes-2.5-mistral-7b.Q8_0.gguf"
MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_FILENAME)

st.set_page_config(page_title="Fraoula LLaMA Chatbot", page_icon="🤖")
st.title("🤖 Fraoula LLaMA Chatbot — Mistral 7B (Hermes Capybara 2.5)")

@st.cache_resource
def download_model():
    os.makedirs(MODEL_DIR, exist_ok=True)
    return hf_hub_download(
        repo_id=REPO_ID,
        filename=MODEL_FILENAME,
        local_dir=MODEL_DIR,
        local_dir_use_symlinks=False
    )

@st.cache_resource
def load_model():
    model_path = download_model()
    return Llama(
        model_path=model_path,
        n_ctx=2048,
        n_threads=2,
        temperature=0.7,
        top_p=0.9,
        stop=["User:", "Bot:"]
    )

llm = load_model()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.text_input("You:", placeholder="Ask me anything...")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    prompt = ""
    for chat in st.session_state.chat_history[-6:]:
        speaker = "User" if chat["role"] == "user" else "Bot"
        prompt += f"{speaker}: {chat['content']}\n"
    prompt += "Bot:"

    bot_output = llm(prompt, max_tokens=512)
    bot_response = bot_output["choices"][0]["text"].strip()

    st.session_state.chat_history.append({"role": "bot", "content": bot_response})

for chat in st.session_state.chat_history:
    speaker = "**You:**" if chat["role"] == "user" else "**Bot:**"
    st.markdown(f"{speaker} {chat['content']}")
