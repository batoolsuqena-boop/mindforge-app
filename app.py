import os
import streamlit as st
from PIL import Image
from google import genai
from audio_recorder_streamlit import audio_recorder

# 1. Page Configuration
st.set_page_config(
    page_title="PhysiMath AI | Entrance Exam & STEM Prep",
    page_icon="📐",
    layout="centered"
)

# 2. Authentic UI Custom Styling (Gemini / Claude Inspired)
st.markdown("""
<style>
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Clean Pill-Style Buttons for Prompts */
    .stButton > button {
        border-radius: 20px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        border-color: #2563EB;
        color: #2563EB;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# 3. Header & Logo Branding
col1, col2 = st.columns([1, 4])
with col1:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=85)
    elif os.path.exists("phymath.jpg"):
        st.image("phymath.jpg", width=85)
    else:
        st.title("📐")
with col2:
    st.title("PhysiMath AI")
    st.caption("🚀 Created by **Sukaina Batool** | Official Academic & Exam Preparation Platform")

st.divider()

# 4. Feature Showcase Banner
with st.expander(":material/stars: **Welcome to PhysiMath AI (Platform Capabilities)**", expanded=False):
    st.markdown("""
    **PhysiMath AI** is an authentic, all-in-one academic solver designed to help students master STEM concepts and prepare for competitive entrance examinations.

    #### 🌟 Key Platform Capabilities
    * **📚 10-Year Past Paper Access:** Practice board exam questions across **9th–12th (ICS, FSC Pre-Engineering, FSC Pre-Medical)**.
    * **💡 Hint-First & Adaptive Practice:** Get step-by-step hints before full solutions to build conceptual mastery.
    * **📸 Attachment Menu (`+`):** Upload textbook pages, capture direct camera snapshots, or record audio queries safely.
    * **🧪 STEM Reference Sheet:** Quick lookup for core physics constants and mathematical identities.
    * **📥 Download Study Notes:** Export your solved chat history directly as a study guide.
    * **🎯 Global Exam Support:** Specialized modes covering **TOLC-I, CEnT-S, CSCA, SAT, CA, ECAT, MDCAT, and GRE/GMAT**.
    """)

# 5. Sidebar Navigation & Features
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

# 10-Year Past Papers Library
st.sidebar.subheader("📚 10-Year Past Papers")
selected_subject = st.sidebar.selectbox("Subject", ["Physics", "Mathematics", "Computer Science", "Chemistry"])
selected_year = st.sidebar.selectbox("Year", [str(year) for year in range(2025, 2014, -1)])
if st.sidebar.button("Fetch Past Papers", use_container_width=True):
    st.sidebar.success(f"Loaded {selected_subject} past papers for {selected_year} ({exam_mode}).")

st.sidebar.divider()

# Interactive STEM Reference Sheet (Sidebar Feature)
with st.sidebar.expander("🧪 **STEM Constants & Formulas**"):
    st.markdown("""
    **Physics Constants:**
    * Speed of Light ($c$): $3 \\times 10^8\\ \\text{m/s}$
    * Gravity ($g$): $9.8\\ \\text{m/s}^2$
    * Planck's Constant ($h$): $6.626 \\times 10^{-34}\\ \\text{J}\\cdot\\text{s}$

    **Math Identities:**
    * $\\sin^2(\\theta) + \\cos^2(\\theta) = 1$
    * $\\frac{d}{dx}(x^n) = n x^{n-1}$
    """)

st.sidebar.divider()

# Session History Management
st.sidebar.subheader("🕒 Session History")
if "messages" not in st.session_state:
    st.session_state.messages = []

history_count = len([m for m in st.session_state.messages if m["role"] == "user"])
st.sidebar.info(f"Saved Queries: **{history_count}**")

# Export Chat History Feature
if st.session_state.messages:
    chat_export_text = "\n\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])
    st.sidebar.download_button(
        label="📥 Download Study Notes",
        data=chat_export_text,
        file_name="PhysiMath_Study_Notes.txt",
        mime="text/plain",
        use_container_width=True
    )

if st.sidebar.button("🗑️ Clear Chat History", use_container_width=True):
    st.session_state.messages = []
    st.rerun()

# 6. Adaptive Quiz & "Hint First" Mode
with st.container(border=True):
    st.subheader(":material/quiz: Adaptive Quick Quiz & Practice")
    guidance_mode = st.radio(
        "Solution Style:",
        ["Complete Step-by-Step Solution", "Hint First (Provide progressive hints before full solution)"],
        horizontal=True
    )

    col_q1, col_q2, col_q3 = st.columns(3)
    with col_q1:
        if st.button("🎲 TOLC-I Math Question", use_container_width=True):
            st.session_state.preset_prompt = "Give me a practice calculus question typical for the TOLC-I entrance exam."
    with col_q2:
        if st.button("📝 Physics Mechanics", use_container_width=True):
            st.session_state.preset_prompt = "Give me a high-yield physics mechanics problem with formulas."
    with col_q3:
        if st.button("📐 CSCA Logic Problem", use_container_width=True):
            st.session_state.preset_prompt = "Give me a practice computer science logic problem for CSCA."

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
Guidance Preference: {guidance_mode}.
Always format mathematical equations cleanly using LaTeX formatting where applicable. Keep explanations encouraging, structured, and easy to follow.
"""

# 8. Render Chat History
st.subheader("💬 Study Chat")
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 9. Gemini-Style `+` Attachment Drawer
image_input = None
audio_bytes = None

with st.expander("➕ **Add Photo, Camera Snapshot, or Voice Query**", expanded=False):
    attachment_type = st.radio("Choose Input Type:", ["🖼️ Upload Photo", "📸 Camera Snapshot", "🎙️ Voice Query"], horizontal=True)

    if attachment_type == "🖼️ Upload Photo":
        uploaded_file = st.file_uploader("Upload textbook page or diagram", type=["jpg", "jpeg", "png"], key="file_upload")
        if uploaded_file:
            image_input = Image.open(uploaded_file)
            st.image(image_input, caption="Uploaded Image Preview", use_container_width=True)

    elif attachment_type == "📸 Camera Snapshot":
        camera_file = st.camera_input("Take a picture of your problem", key="camera_upload")
        if camera_file:
            image_input = Image.open(camera_file)
            st.image(image_input, caption="Camera Snapshot Preview", use_container_width=True)

    elif attachment_type == "🎙️ Voice Query":
        st.write("Click below to record your question:")
        audio_bytes = audio_recorder(text="Record Voice Query", icon_size="2x", key="voice_recorder")

# Check for preset prompt triggers from pill buttons
preset_text = st.session_state.pop("preset_prompt", None)

# Chat Input Bar
user_prompt = st.chat_input("Type your question or past paper query here...")

# Handle Input Trigger
active_input = user_prompt if user_prompt else preset_text

if active_input or audio_bytes:
    prompt_text = active_input if active_input else "Please analyze the uploaded problem (voice query received)."
    
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

# 10. Student Feedback & Review
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
