import os
import streamlit as st
import pdfplumber
from dotenv import load_dotenv
from gemini_helper import extract_resume_info, generate_questions, get_feedback

# Load environment variables to check API key
load_dotenv(override=True)
api_key = os.getenv("GEMINI_API_KEY")

# Sidebar - Title, Instructions, and Reset Control
st.sidebar.title("Interview Prep Bot 🤖")
st.sidebar.markdown("""
### How to Use:
1. **Upload Resume**: Upload a text-based PDF resume using the file uploader.
2. **Analyze Resume**: Click **Analyze Resume** to parse structured details (skills, projects, experience, education).
3. **Generate Questions**: Click **Generate Interview Questions** to get 8 tailored practice questions.
4. **Answer & Submit**: Type your answers to the questions and click **Submit Answer** to get constructive coaching feedback and scores.
""")

# Start Over Button
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Start Over", use_container_width=True):
    st.session_state.clear()
    st.success("App reset successfully!")
    st.rerun()

st.title("Interview Preparation Bot")

# Error Handling: Missing Gemini API Key
if not api_key:
    st.error("⚠️ **Gemini API Key is missing!** Please add your `GEMINI_API_KEY` to the `.env` file in the project root folder to use this app.")
    st.stop()

# Initialize session state for extracted text, analysis, questions, and feedback
if "extracted_text" not in st.session_state:
    st.session_state.extracted_text = None
if "file_key" not in st.session_state:
    st.session_state.file_key = None
if "resume_analysis" not in st.session_state:
    st.session_state.resume_analysis = None
if "interview_questions" not in st.session_state:
    st.session_state.interview_questions = None
if "answers_feedback" not in st.session_state:
    st.session_state.answers_feedback = {}

# File Uploader
uploaded_file = st.file_uploader("Upload your resume or PDF document", type=["pdf"])

if uploaded_file is not None:
    # Use a unique key based on filename and size to check if it's a new upload
    current_file_key = f"{uploaded_file.name}_{uploaded_file.size}"
    if st.session_state.file_key != current_file_key:
        with st.spinner("Extracting text from PDF..."):
            try:
                text_content = []
                with pdfplumber.open(uploaded_file) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_content.append(page_text)
                
                extracted_raw = "\n".join(text_content).strip()
                
                # Error Handling: Empty resume upload
                if not extracted_raw:
                    st.error("❌ **Empty Resume / No Text Extracted**: The uploaded PDF does not contain extractable text. Please upload a digital PDF (not a scanned image or empty document).")
                    st.session_state.extracted_text = None
                    st.session_state.file_key = None
                    st.session_state.resume_analysis = None
                    st.session_state.interview_questions = None
                    st.session_state.answers_feedback = {}
                else:
                    st.session_state.extracted_text = extracted_raw
                    st.session_state.file_key = current_file_key
                    # Clear previous state since a new file is uploaded
                    st.session_state.resume_analysis = None
                    st.session_state.interview_questions = None
                    st.session_state.answers_feedback = {}
                    st.success("PDF text successfully extracted!")
            except Exception as e:
                st.error(f"Error extracting PDF text: {e}")
                st.session_state.extracted_text = None
                st.session_state.file_key = None
                st.session_state.resume_analysis = None
                st.session_state.interview_questions = None
                st.session_state.answers_feedback = {}
else:
    # Clear state when file is removed
    st.session_state.extracted_text = None
    st.session_state.file_key = None
    st.session_state.resume_analysis = None
    st.session_state.interview_questions = None
    st.session_state.answers_feedback = {}

# Display the extracted text in an expander if available
if st.session_state.extracted_text is not None:
    with st.expander("Verify Extracted Text", expanded=False):
        st.text(st.session_state.extracted_text)
        
    # Button to trigger Gemini API analysis
    if st.button("Analyze Resume", type="primary"):
        with st.spinner("Analyzing resume text..."):
            try:
                analysis = extract_resume_info(st.session_state.extracted_text)
                st.session_state.resume_analysis = analysis
                st.session_state.interview_questions = None  # reset questions for new analysis
                st.session_state.answers_feedback = {}  # reset feedback for new analysis
                st.success("Analysis complete!")
            except Exception as e:
                st.error(f"Analysis failed: {e}")

# Display the parsed information if available
if st.session_state.resume_analysis is not None:
    analysis = st.session_state.resume_analysis
    
    st.markdown("---")
    st.header("Resume Profile")
    
    # 2-column layout for profile details
    col1, col2 = st.columns(2)
    
    with col1:
        # 1. Skills
        st.subheader("Skills")
        skills = analysis.get("skills", [])
        if skills:
            for skill in skills:
                st.write(f"- {skill}")
        else:
            st.write("No skills found.")
            
        # 3. Experience
        st.subheader("Experience")
        experience = analysis.get("experience", [])
        if experience:
            for exp in experience:
                role = exp.get("role", "N/A")
                company = exp.get("company", "N/A")
                desc = exp.get("description", "")
                st.write(f"- **{role}** at *{company}*:\n  {desc}")
        else:
            st.write("No experience details found.")
            
    with col2:
        # 2. Projects
        st.subheader("Projects")
        projects = analysis.get("projects", [])
        if projects:
            for proj in projects:
                st.write(f"- **{proj.get('name', 'N/A')}**:\n  {proj.get('description', '')}")
        else:
            st.write("No projects found.")
            
        # 4. Education
        st.subheader("Education")
        education = analysis.get("education", [])
        if education:
            for edu in education:
                st.write(f"- {edu}")
        else:
            st.write("No education details found.")
            
    # Generate Questions Section
    st.markdown("---")
    st.header("Interview Practice Questions")
    
    if st.button("Generate Interview Questions", type="secondary"):
        with st.spinner("Generating 8 tailored interview questions..."):
            try:
                questions = generate_questions(st.session_state.resume_analysis)
                st.session_state.interview_questions = questions
                st.session_state.answers_feedback = {}  # reset feedback for new questions
                st.success("Questions generated successfully!")
            except Exception as e:
                st.error(f"Failed to generate questions: {e}")
                
    if st.session_state.interview_questions is not None:
        questions = st.session_state.interview_questions
        for i, q in enumerate(questions, 1):
            with st.container():
                difficulty = q.get('difficulty', 'Medium')
                
                # Choose color styling based on difficulty level
                if difficulty.lower() == 'easy':
                    badge_style = "background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb;"
                elif difficulty.lower() == 'hard':
                    badge_style = "background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb;"
                else:
                    badge_style = "background-color: #fff3cd; color: #856404; border: 1px solid #ffeeba;"
                
                st.markdown(f"### Q{i}: {q.get('question')}")
                
                badge_html = f'<span style="{badge_style} padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; display: inline-block;">{difficulty}</span>'
                st.markdown(f"**Topic**: {q.get('topic')} &nbsp;|&nbsp; {badge_html}", unsafe_allow_html=True)
                
                # Input for the user's answer, uniquely keyed
                user_ans = st.text_area(
                    "Your Answer:",
                    key=f"user_answer_{i}",
                    placeholder="Type your answer here...",
                    height=100
                )
                
                # Submit Answer Button
                if st.button("Submit Answer", key=f"submit_answer_{i}"):
                    if not user_ans.strip():
                        st.warning("Please type your answer before submitting.")
                    else:
                        with st.spinner("Evaluating response..."):
                            try:
                                feedback_res = get_feedback(
                                    question=q.get('question'),
                                    model_answer=q.get('model_answer'),
                                    user_answer=user_ans
                                )
                                st.session_state.answers_feedback[i] = feedback_res
                            except Exception as e:
                                st.error(f"Failed to get feedback: {e}")
                
                # If feedback exists for this question, display it
                if i in st.session_state.answers_feedback:
                    feedback_data = st.session_state.answers_feedback[i]
                    score = feedback_data.get("score", 0)
                    feedback_text = feedback_data.get("feedback", "")
                    
                    # Style the score display
                    if score >= 7:
                        score_style = "color: #28a745; font-weight: bold; font-size: 1.25rem;"
                    elif score <= 4:
                        score_style = "color: #dc3545; font-weight: bold; font-size: 1.25rem;"
                    else:
                        score_style = "color: #fd7e14; font-weight: bold; font-size: 1.25rem;"
                        
                    st.markdown(f'<div style="background-color: #f8f9fa; border-left: 4px solid #007bff; padding: 12px; border-radius: 4px; margin-top: 10px; margin-bottom: 10px;">'
                                f'<p style="margin: 0; font-weight: bold;">Evaluation</p>'
                                f'<p style="margin: 5px 0;">Score: <span style="{score_style}">{score}/10</span></p>'
                                f'<p style="margin: 0; font-style: italic;">{feedback_text}</p>'
                                f'</div>', unsafe_allow_html=True)
                    
                    with st.expander("Show Model Answer", expanded=True):
                        st.write(q.get('model_answer'))
                st.write("")
