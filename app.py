import streamlit as st
from google import genai
from PIL import Image

# 1. Page Configuration & Title
st.set_page_config(page_title="PhysiMath AI", page_icon="📐", layout="centered")
st.title("📐 PhysiMath AI")
st.caption("Your Step-by-Step Mathematics & Physics Exam Assistant")

# 2. Sidebar: Exam Selector & Image Uploader
st.sidebar.header("🎯 Exam Preparation Mode")
exam_mode = st.sidebar.selectbox(
    "Choose target examination:",
    ["General Math & Physics", "TOLC-I", "CEnT-S", "CSCA", "CA"]
)
st.sidebar.info(f"Configured for **{exam_mode}** syllabus.")

st.sidebar.header("📷 Upload Textbook / Problem Photo")
uploaded_file = st.sidebar.file_uploader(
    "Upload picture of problem", 
    type=["jpg", "jpeg", "png"]
)

image_input = None
if uploaded_file is not None:
    image_input = Image.open(uploaded_file)
    st.sidebar.image(image_input, caption="Uploaded Problem", use_container_width=True)

# 3. Initialize Gemini Client using Streamlit secrets
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("Missing GEMINI_API_KEY in secrets.")
    st.stop()

client = genai.Client(api_key=api_key)

# 4. System Instruction for Math & Physics Tutor
system_instruction = f"""
You are PhysiMath AI, an expert Professor of Mathematics and Physics specializing in international entrance exams ({exam_mode}).
Guidelines:
- Solve problems step-by-step.
- Display relevant formulas first before calculations.
- Explain core concepts clearly.
- For exams like TOLC-I, CEnT-S, or CSCA, highlight shortcuts and key test strategies.
"""

# 5. Session State for Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display past messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 6. Chat Input & Processing
if user_prompt := st.chat_input("Ask a question or explain the uploaded photo..."):
    # Display user message
    st.chat_message("user").markdown(user_prompt)
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    # Prepare input payload (handles both image and text)
    contents = []
    if image_input:
        contents.append(image_input)
    contents.append(user_prompt)

    with st.chat_message("assistant"):
        with st.spinner("Solving step-by-step..."):
            try:
                response = client.models.generate_content(
                  model="gemini-2.5-flash",
                    contents=contents,
                    config={"system_instruction": system_instruction}
                )
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Error: {e}")
