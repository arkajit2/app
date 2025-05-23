import streamlit as st
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Load model and tokenizer
@st.cache_resource
def load_model():
    model_id = "meta-llama/Meta-Llama-3-8B-Instruct"
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        device_map="auto"
    )
    return tokenizer, model

tokenizer, model = load_model()

# Set up UI
st.title("🦙 LLaMA 3 Chatbot (Local)")
st.markdown("Ask anything, powered by Meta's LLaMA 3 model.")

# Session state for conversation
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Chat input
user_input = st.text_input("You:", key="input")

def generate_response(user_prompt, history):
    # Format as chat history
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    for u, a in history:
        messages.append({"role": "user", "content": u})
        messages.append({"role": "assistant", "content": a})
    messages.append({"role": "user", "content": user_prompt})

    input_ids = tokenizer.apply_chat_template(messages, return_tensors="pt").to(model.device)
    outputs = model.generate(input_ids, max_new_tokens=512, do_sample=True, temperature=0.7)
    decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Extract last assistant response
    response = decoded.split("assistant")[-1].strip()
    return response

# Display chat
for user, bot in st.session_state.chat_history:
    st.markdown(f"**You**: {user}")
    st.markdown(f"**LLaMA 3**: {bot}")

# Handle new input
if user_input:
    with st.spinner("Thinking..."):
        answer = generate_response(user_input, st.session_state.chat_history)
        st.session_state.chat_history.append((user_input, answer))
        st.experimental_rerun()
