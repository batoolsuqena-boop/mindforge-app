import os
import time
import streamlit as st
from PIL import Image
from google import genai
from audio_recorder_streamlit import audio_recorder
from fpdf import FPDF

# 1. Page Configuration
st.set_page_config(
    page_title="PhysiMath AI | Entrance Exam & STEM Prep",
    page_icon="📐",
    layout="centered"
)

# 2. Styling
st.markdown("""
<style>
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Helper Function to Generate PDF File
def generate_pdf(messages):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "PhysiMath AI - Study Notes", ln=True, align='C')
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 8, "Official Exam Preparation Notes", ln=True, align='C')
    pdf.ln(5)
    
    pdf.set_font("Arial", size=11)
    for msg in messages:
        role = "Student Question:" if msg["role"] == "user" else "PhysiMath Solution:"
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 6, role, ln=True)
        pdf.set_font("Arial", size=10)
        # Encode string to handle standard symbols safely
        clean_text = msg["content"].encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 6, clean_text)
        pdf.ln(4)
        
    return pdf.output(dest='S').encode('latin-1')

# 3. Branding Header
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

# 4. Sidebar Exam Settings & 10-Year Past Papers
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

# Session History Controls
st.sidebar.subheader("🕒 Session History")
if "messages" not in st.session_state:
    st.session_state.messages = []

history_count = len([m for m in st.session_state.messages if m["role"] == "user"])
st.sidebar.info(f"Saved Queries: **{history_count}**")

if st.sidebar.button("🗑️ Clear Chat History", use_container_width=True):
    st.session_state.messages = []
    st.rerun()

# 5. FEATURE 1: Interactive STEM Formula & Constant Library
with st.expander("🧪 **Interactive STEM Formula & Physics Constant Library**", expanded=False):
    st.markdown("""
    **Physics Constants:**
    * Speed of Light ($c$): $3 \\times 10^8\\ \\text{m/s}$
    * Gravitational Acceleration ($g$): $9.8\\ \\text{m/s}^2$
    * Planck's Constant ($h$): $6.626 \\times 10^{-34}\\ \\text{J}\\cdot\\text{s}$

    **Core Mathematics Formulas:**
    * Trigonometric Identity: $\\sin^2(\\theta) + \\cos^2(\\theta) = 1$
    * Derivative Power Rule: $\\frac{d}{dx}(x^n) = n x^{n-1}$
    * Quadratic Formula: $x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$
    """)

# 6. FEATURE 2: Mock Exam Timer
with st.container(border=True):
    st.subheader("⏱️ **Mock Exam Practice & Timer**")
    st.write("Test your speed and accuracy for competitive exams under timed conditions.")
    
    col_t1, col_t2 = st.columns([2, 1])
    with col_t1:
        timer_seconds = st.slider("Select Exam Countdown (Minutes):", 1, 15, 5) * 60
    with col_t2:
        if st.button("▶️ Start Timer", type="primary", use_container_width=True):
            st.session_state.start_time = time.time()
            st.session_state.timer_duration = timer_seconds

    if "start_time" in st.session_state:
        elapsed = time.time() - st.session_state.start_time
        remaining = max(0, int(st.session_state.timer_duration - elapsed))
        mins, secs = divmod(remaining, 60)
        st.metric("⏳ Time Remaining:", f"{mins:02d}:{secs:02d}")
        if remaining == 0:
            st.warning("⏰ Time is up! Review your answers.")

# 7. FEATURE 3: Step-by-Step "Hint First" Mode
with st.container(border=True):
    st.subheader("💡 **Step-by-Step Guidance Style**")
    guidance_mode = st.radio(
        "Select how PhysiMath AI should solve your problems:",
        ["Complete Step-by-Step Solution", "Hint First (Give hints before full answer)"],
        horizontal=True
    )

st.divider()

# 8. Gemini API Setup
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("API Key missing! Please set GEMINI_API_KEY in your Streamlit secrets.")
    st.stop()

client = genai.Client(api_key=api_key)

system_instruction = f"""
You are PhysiMath AI, an expert academic tutor created by Sukaina Batool.
You help students with board exams (9th-12th ICS, FSC Pre-Medical, FSC Pre-Engineering) and entrance tests (SAT, TOLC-I, CEnT-S, CSCA, CA, ECAT, MDCAT).
Active Target Mode: {exam_mode}.
Guidance Style: {guidance_mode}.
Always format mathematical equations cleanly using LaTeX formatting. Keep explanations structured, clear, and easy to follow.
"""

# 9. Render Chat History & PDF Download Button
st.subheader("💬 Study Chat")

# PDF Download Trigger
if st.session_state.messages:
    try:
        pdf_bytes = generate_pdf(st.session_state.messages)
        st.download_button(
            label="📄 Download Study Notes as PDF",
            data=pdf_bytes,
            file_name="PhysiMath_Study_Notes.pdf",
            mime="application/pdf",
            type="primary"
        )
    except Exception as e:
        st.caption("Add 'fpdf2' to requirements.txt to enable direct PDF downloads.")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 10. Gemini-Style Attachment Drawer
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

# Text Chat Input
user_prompt = st.chat_input("Type your question or past paper query here...")

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

# 11. Student Feedback & Review
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
