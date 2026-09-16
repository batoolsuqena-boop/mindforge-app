import os
import streamlit as st
from PIL import Image
from google import genai
from audio_recorder_streamlit import audio_recorder

# Page Configuration
st.set_page_config(page_title="PhysiMath AI", page_icon="📐", layout="centered")

# Display Logo and Title Header
col1, col2 = st.columns([1, 4])
with col1:
    if os.path.exists("phymath.jpg"):
        st.image("phymath.jpg", width=100)
    else:
        st.title("📐")
with col2:
    st.title("PhysiMath AI")
    st.caption("🚀 Created by **Sukaina Batool** | Your AI Assistant for Entrance Exam Success")

st.divider()

# Interactive Welcome & Feature Introduction Banner
with st.expander("✨ **Welcome to PhysiMath AI! (How This App Helps You)**", expanded=True):
    st.markdown("""
    Welcome! **PhysiMath AI** is designed specifically to help students excel in high-stakes Mathematics and Physics entrance examinations (such as **TOLC-I, CEnT-S, CSCA, and CA**).
    
    ### 🌟 What Makes PhysiMath AI Different?
    * **👨‍💻 Created for Students:** Built by **Sukaina Batool** to provide tailored, high-yield exam preparation guidance.
    * **📸 Visual Problem Solving:** Upload photos of textbook pages, handwritten physics derivations, or math diagrams for instant step-by-step breakdown.
    * **🎙️ Voice & Text Input:** Ask your questions by typing or recording your voice directly into the app!
    * **🎯 Focused STEM Expertise:** Unlike generic AI tools, PhysiMath AI focuses strictly on core concepts, formulas, unit conversions, and exam rigor.
    """)

# Sidebar Navigation & Settings
st.sidebar.header("⚙️ Exam Settings")
exam_mode = st.sidebar.selectbox(
    "Target Exam Mode",
    ["General Math & Physics", "TOLC-I Prep", "CEnT-S Prep", "CSCA Prep", "CA Prep"]
)
st.sidebar.info(f"Active Mode: **{exam_mode}**\n\nOptimized for step-by-step solution steps.")

# Gemini API Client Setup
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("API Key missing! Please set GEMINI_API_KEY in your Streamlit secrets.")
    st.stop()

client = genai.Client(api_key=api_key)

# System Instruction Persona
system_instruction = f"""
You are PhysiMath AI, an expert Mathematics and Physics tutor created by Sukaina Batool.
Your primary role is to help students prepare for entrance exams such as TOLC-I, CEnT-S, CSCA, and CA.
Always explain problems step-by-step, showing intermediate formulas, unit conversions, and clear logic.
Currently active target mode: {exam_mode}.
Keep explanations concise, encouraging, and clear.
"""

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render Previous Messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# File Uploader for Image Input
uploaded_file = st.file_uploader("📸 Upload Textbook or Problem Photo", type=["jpg", "jpeg", "png"])
image_input = None
if uploaded_file:
    image_input = Image.open(uploaded_file)
    st.image(image_input, caption="Uploaded Image Preview", use_container_width=True)

# Audio Recorder for Voice Interaction
st.write("🎙️ **Ask with your voice:**")
audio_bytes = audio_recorder(text="Click to record question", icon_size="2x")

# Handle Inputs
user_prompt = st.chat_input("Ask a question or explain the uploaded photo...")

# Process Input (Text or Audio)
if user_prompt or audio_bytes:
    prompt_text = user_prompt if user_prompt else "Please analyze the uploaded problem (voice query received)."
    
    # Display user message
    st.chat_message("user").markdown(prompt_text)
    st.session_state.messages.append({"role": "user", "content": prompt_text})

    # Prepare input payload
    contents = []
    if image_input:
        contents.append(image_input)
    contents.append(prompt_text)

    # Generate Response from Gemini
    with st.chat_message("assistant"):
        with st.spinner("Solving step-by-step..."):
            try:
                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=contents,
                    config={"system_instruction": system_instruction}
                )
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Error: {e}")
