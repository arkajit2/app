if "input_text" not in st.session_state:
    st.session_state["input_text"] = ""

user_input = st.text_input("You:", placeholder="Type your message...", key="input_text")

if send_button and user_input.strip():
    st.session_state.chat_history.append({"role": "user", "content": user_input.strip()})
    with st.spinner("Thinking..."):
        reply = get_gemini_response(user_input.strip(), st.session_state.chat_history)
    st.session_state.chat_history.append({"role": "assistant", "content": reply})

    # Clear the input box by setting the session state variable to empty string
    st.session_state["input_text"] = ""

    # Rerun app to reflect changes
    st.experimental_rerun()
