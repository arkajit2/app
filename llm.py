import streamlit as st
from transformers import pipeline, set_seed

st.title("Fraoula LLM Chatbot")

# Initialize the generator once
@st.cache_resource
def get_generator():
    set_seed(42)
    return pipeline('text-generation', model='distilgpt2')

generator = get_generator()

prompt = st.text_input("You:", "Hello, who are you?")
if prompt:
    output = generator(prompt, max_length=100, num_return_sequences=1)
    st.write("Bot:", output[0]['generated_text'])
