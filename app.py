import streamlit as st
from google import genai

st.set_page_config(page_title="MindForge AI App", page_icon="⚡")

st.title("⚡ MindForge AI Chat")

# Check Streamlit Secrets first, otherwise check sidebar
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

st.divider()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask AI anything..."):
    if not api_key:
        st.error("Please enter your Gemini API Key in the sidebar.")
    else:
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        try:
            client = genai.Client(api_key=api_key)
            # Updated model name here
            chat = client.chats.create(model="gemini-3.6-flash")
            response = chat.send_message(prompt)

            with st.chat_message("assistant"):
                st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error(f"Error: {e}")