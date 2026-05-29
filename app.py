# app.py
import streamlit as st
import anthropic

# 1. Setup Page Configurations
st.set_page_config(page_title="AI Resume Tailor", page_icon="📝", layout="centered")

# 2. Basic Gatekeeper Authentication
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔒 Access Restricted")
    user_password = st.text_input("Enter the access password:", type="password")
    if st.button("Unlock Tool"):
        if user_password == st.secrets["APP_PASSWORD"]:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Incorrect password. Please try again.")
    st.stop()

# 3. Initialize Claude Client securely using Secrets
client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

st.title("📝 Custom Resume Tailoring Assistant")
st.write("Paste a job description below to align your experience perfectly with what recruiters are seeking.")

# 4. User Inputs
# Hardcode your actual master resume text inside the triple quotes below so they don't have to re-paste it.
MASTER_RESUME = """
[PASTE YOUR FULL MASTER RESUME EXPERIENCE, EDUCATION, AND SKILLS HERE]
"""

st.subheader("Target Job Parameters")
job_title = st.text_input("Job Title", placeholder="e.g., Senior Project Coordinator")
job_description = st.text_area("Paste the Job Description here:", height=250)

# 5. Execution Trigger
if st.button("Generate Tailored Resume", type="primary"):
    if not job_description:
        st.warning("Please provide a job description to initiate the optimization process.")
    else:
        with st.spinner("Claude is analyzing requirements and rewriting keywords..."):
            try:
                # System instructions ensuring structural integrity and preventing AI hallucinations
                prompt_content = f"""
                You are an expert technical resume writer. Your task is to customize the provided Master Resume to align perfectly with the target Job Description.
                
                Guidelines:
                1. Do not invent false experience, tools, metrics, or certifications.
                2. Dynamically prioritize and highlight the skills, tools, and technical competencies listed in the Master Resume that map directly to the target responsibilities.
                3. Rewrite bullet points to mirror the professional vocabulary and action verbs used in the job description while maintaining the truth of the original metrics.
                4. Output ONLY the beautifully formatted markdown of the new resume. Do not include any chat commentary or conversational padding.
                
                Target Job Title: {job_title}
                
                Target Job Description:
                {job_description}
                
                Master Resume Base:
                {MASTER_RESUME}
                """

                # Call Claude (Sonnet 3.5 is the standard gold-medal choice for processing complex mapping instructions)
                message = client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=4000,
                    temperature=0.2,
                    messages=[
                        {"role": "user", "content": prompt_content}
                    ]
                )
                
                # Extract output response string
                customized_resume = message.content[0].text
                
                st.success("✨ Optimization Complete!")
                st.markdown("### Your Tailored Resume")
                st.markdown(customized_resume)
                
                # Add a quick download option for the raw Markdown text file
                st.download_button(
                    label="Download Markdown File",
                    data=customized_resume,
                    file_name=f"Resume_{job_title.replace(' ', '_') if job_title else 'Tailored'}.md",
                    mime="text/markdown"
                )

            except Exception as e:
                st.error(f"An infrastructure error occurred during generation: {e}")