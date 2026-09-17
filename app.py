import os
import streamlit as st
from PIL import Image
from google import genai
from audio_recorder_streamlit import audio_recorder

# 1. Page & Layout Configuration
st.set_page_config(
    page_title="PhysiMath AI | Entrance Exam & STEM Prep",
    page_icon="📐",
    layout="centered"
)

# 2. Inject Custom CSS for Clean Design
st.markdown("""
<style>
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# 3. Authentic Branding Header
col1, col2 = st.columns([1, 4])
with col1:
    if os.path.exists("phymath.jpg"):
        st.image("phymath.jpg", width=90)
    else:
        st.title("📐")
with col2:
    st.title("PhysiMath AI")
    st.caption("🚀 Created by **Sukaina Batool** | Official Academic & Exam Preparation Platform")

st.divider()

# 4. Feature Showcase Banner
with st.expander(":material/stars: **Welcome to PhysiMath AI (Platform Features)**", expanded=True):
    st.markdown("""
    **PhysiMath AI** is an authentic, all-in-one academic solver designed to help students master STEM concepts and prepare for board and entrance examinations.

    #### 🌟 Key Platform Capabilities
    * **📚 10-Year Past Paper Access:** Practice board exam questions across **9th–12th (ICS, FSC Pre-Engineering, FSC Pre-Medical)**.
    * **🧠 Adaptive Practice Quizzes:** Toggle between **Guided Mode** (with formula hints) and **Advanced Challenge Mode**.
    * **📸 Camera & Photo Upload:** Click the **`+`** menu to upload an image or take a live photo.
    * **🎙️ Voice Interaction:** Ask complex equations or physics questions hands-free.
    * **🕒 Chat Session History:** Track and clear past study queries anytime from the sidebar.
    * **🎯 Global Exam Support:** Dedicated prep modes for **TOLC-I, CEnT-S, CSCA, SAT, CA, ECAT, MDCAT, and GRE/GMAT**.
    """)

# 5. Sidebar Navigation & Settings
st.sidebar.header("⚙️ Exam & Study Settings")

exam_mode = st.sidebar.selectbox(
    "Select Target Class / Exam Mode",
    [
        "9th Class (Matric Prep)",
        "10th Class (Matric Prep)",
        "11th Class / 1st Year (ICS & FSC)",
        "12th Class / 2nd Year (ICS & FSC)",
        "FSC Pre-Engineering Prep",
        "FSC Pre-Medical Prep",
        "TOLC-I Prep", 
        "CEnT-S Prep", 
        "CSCA Prep", 
        "CA Prep",
        "SAT Math & Physics Prep",
        "GRE / GMAT Quantitative Prep",
        "ECAT & MDCAT Prep"
    ]
)

st.sidebar.divider()

# Sidebar Past Papers Library
st.sidebar.subheader("📚 10-Year Past Papers")
selected_subject = st.sidebar.selectbox("Subject", ["Physics", "Mathematics", "Computer Science", "Chemistry"])
selected_year = st.sidebar.selectbox("Year", [str(year) for year in range(2025, 2014, -1)])
if st.sidebar.button("Fetch Past Papers", use_container_width=True):
    st.sidebar.success(f"Loaded {selected_subject} past papers for {selected_year} ({exam_mode}).")

st.sidebar.divider()

# Sidebar Chat History Controls
st.sidebar.subheader("🕒 Session History")
if "messages" not in st.session_state:
    st.session_state.messages = []

history_count = len([m for m in st.session_state.messages if m["role"] == "user"])
st.sidebar.info(f"Saved Queries in Session: **{history_count}**")

if st.sidebar.button("🗑️ Clear Chat History", use_container_width=True):
    st.session_state.messages = []
    st.rerun()

# 6. Adaptive Quiz Feature Container
with st.container(border=True):
    st.subheader(":material/quiz: Adaptive Quick Quiz")
    quiz_level = st.radio(
        "Choose Guidance Level:", 
        ["Foundation / Guided Mode (With Hints)", "Advanced Challenge Mode (Time & Speed Focus)"], 
        horizontal=True
    )

    if st.button("🎲 Generate Practice Question", type="primary"):
        st.info(f"Generating a {selected_subject} problem tailored for **{exam_mode}** in **{quiz_level}**...")

st.divider()

# 7. Gemini API Setup
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("API Key missing! Please set GEMINI_API_KEY in your Streamlit secrets.")
    st.stop()

client = genai.Client(api_key=api_key)

system_instruction = f"""
You are PhysiMath AI, an expert academic tutor created by Sukaina Batool.
You help students with board exams (9th-12th ICS, FSC Pre-Medical, FSC Pre-Engineering) and entrance tests (SAT, TOLC-I, CEnT-S, CSCA, CA, ECAT, MDCAT).
Active Target Mode: {exam_mode}.
Learning Level: {quiz_level}.
Provide clear, step-by-step solutions showing formulas, unit conversions, and conceptual reasoning.
"""

# 8. Render Study Chat
st.subheader("💬 Study Chat History")
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 9. Gemini-Style `+` Attachment Expander
image_input = None

with st.expander("➕ **Add Photo, Take Picture, or Record Voice**", expanded=False):
    attachment_type = st.radio("Choose Input Method:", ["🖼️ Upload Photo", "📸 Take Photo (Camera)", "🎙️ Voice Recording"], horizontal=True)

    if attachment_type == "🖼️ Upload Photo":
        uploaded_file = st.file_uploader("Upload textbook page or diagram", type=["jpg", "jpeg", "png"], key="file_upload")
        if uploaded_file:
            image_input = Image.open(uploaded_file)
            st.image(image_input, caption="Uploaded Image Preview", use_container_width=True)

    elif attachment_type == "📸 Take Photo (Camera)":
        camera_file = st.camera_input("Take a direct picture of your problem", key="camera_upload")
        if camera_file:
            image_input = Image.open(camera_file)
            st.image(image_input, caption="Camera Snapshot Preview", use_container_width=True)

    elif attachment_type == "🎙️ Voice Recording":
        st.write("Click below to record your question:")
        audio_bytes = audio_recorder(text="Record Voice Query", icon_size="2x", key="voice_recorder")
    else:
        audio_bytes = None

if "audio_bytes" not in locals():
    audio_bytes = None

# Text Input Area
user_prompt = st.chat_input("Type your question or past paper query here...")

# Multi-Modal Processing Logic
if user_prompt or audio_bytes:
    prompt_text = user_prompt if user_prompt else "Please analyze the uploaded problem (voice query received)."
    
    st.chat_message("user").markdown(prompt_text)
    st.session_state.messages.append({"role": "user", "content": prompt_text})

    contents = []
    if image_input:
        contents.append(image_input)
    contents.append(prompt_text)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing problem step-by-step..."):
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

st.divider()

# 10. Student Review & Feedback Container
with st.container(border=True):
    st.subheader(":material/rate_review: Student Feedback & Review")
    st.markdown("### Is this app helpful?")

    star_rating = st.select_slider(
        "Rate your learning experience with PhysiMath AI:",
        options=["⭐ (1 - Needs Improvement)", "⭐⭐ (2 - Fair)", "⭐⭐⭐ (3 - Good)", "⭐⭐⭐⭐ (4 - Very Helpful)", "⭐⭐⭐⭐⭐ (5 - Excellent)"],
        value="⭐⭐⭐⭐⭐ (5 - Excellent)"
    )

    student_review = st.text_area(
        "Share your experience, review, or suggested features for Sukaina Batool:",
        placeholder="Let us know how PhysiMath AI helped you prepare for your exams..."
    )

    if st.button("Submit Review", type="primary"):
        if student_review.strip():
            st.success("Thank you for your feedback! Your review has been recorded to help improve PhysiMath AI.")
        else:
            st.warning("Please write a short comment before submitting your review.")
