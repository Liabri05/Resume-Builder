# app.py
import streamlit as st
import anthropic
import time

#Page Config
st.set_page_config(page_title="AI Resume Tailor", page_icon="📝", layout="centered")

# Basic Authentication
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

#Initialize Claude using Secrets
client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

st.title("📝 Custom Resume Tailoring Assistant")
st.write("Paste a job description below to align your experience perfectly with what recruiters are seeking.")

#User Inputs
# Hardcode your actual master resume text inside the triple quotes below so they don't have to re-paste it.
MASTER_RESUME = """
[
Pedro Pettenazzi
Porto, Portugal
pedrohpettenazzi@email.com
linkedin.com/in/pedro-pettenazzi-4486053a4

EXPERIENCE
Consumer Analytics Specialist — Airbnb (2022 through 2025 | Remote)
Extract actionable insights from high-volume consumer behavioral data to enhance user journeys and search intent.
● Own the day-to-day tracking of operational KPIs to keep marketing budgets efficient and ensure every campaign meets 100% of our compliance standards.
Tools: Python · Looker Studio · Excel · Adobe · Jamovi · R 
RWS Group Remote
Content Localization Copyeditor (EN>PT) Nov 2024 - Aug 2025
● Edited and localized AI-generated content for accuracy, tone, and cultural relevance.
● Collaborated with cross-border editorial teams on large-scale content localization projects.
● Ensured strict adherence to complex client style guides and regulatory specifications for localized content.
Freelance Remote
Kantar Consulting Porto,Portugal
Marketing Strategy (Intern) Summer 2024
● Designed data-informed internal campaigns that increased participation and engagement by 60% through behavioral analysis and audience segmentation.
● Translated complex data reports into strategic briefs for cross-functional teams, aligning commercial outcomes with market trends and optimizing for conversions.
Designed data-informed internal campaigns that successfully increased participation and engagement by 57% through behavioral analysis.
● Translated complex data reports into strategic briefs used by diverse departments to align commercial outcomes with market trends.
Tools: SQL · Excel

CERTIFICATIONS 
Google Ads
Google Digital Garage Marketing
Google Analytics

EDUCATION
MBA — Marketing & Business Analytics | IPAM The Marketing School (2020 through 2022 | Porto, Portugal)
Thesis: "Integration of Artificial Intelligence in Consumer Purchase Decisions in Portugal" — original research into how AI-driven personalization shapes buying behavior across Portuguese consumer segments.
BA — Communication Sciences: Journalism, Multimedia, Public Relations | Universidade do Porto (2016 through 2020 | Porto, Portugal)

SKILLS
Data & Analytics: Python · Microsoft Excel · Looker Studio · Data Visualization · Consumer Analytics · Market Research
Strategy & Business: Business Strategy · Strategic Planning · Market Intelligence · Competitive Analysis · Consumer Behaviour · Business Analysis
Risk & Operations: Risk Management · Vendor Management · Operational Reporting · Audit Support · Compliance · Process Improvement
Communication & Research: Content Strategy · Copywriting · Research & Insights · Data Storytelling · Stakeholder Presentations · Report Writing
Languages: English (fluent) · Portuguese (native)]
"""

st.subheader("Target Job Parameters")
job_title = st.text_input("Job Title", placeholder="e.g., Senior Project Coordinator")
job_description = st.text_area("Paste the Job Description here:", height=250)

MAX_REQUESTS = 1
TIME_WINDOW = 60  # in seconds

# Initialize a tracking list in the user's session (unless it already exists)
if "request_timestamps" not in st.session_state:
    st.session_state["request_timestamps"] = []

# Trigger 
if st.button("Generate Tailored Resume", type="primary"):
    if not job_description:
        st.warning("Please provide a job description to initiate the optimization process.")
    else:
        # CHECK THE RATE LIMIT
        current_time = time.time()
        
        # Clean timestamps older than 60s
        st.session_state["request_timestamps"] = [
            t for t in st.session_state["request_timestamps"] if current_time - t < TIME_WINDOW
        ]
        
        # check threshold
        if len(st.session_state["request_timestamps"]) >= MAX_REQUESTS:
            oldest_request = st.session_state["request_timestamps"][0]
            seconds_left = int(TIME_WINDOW - (current_time - oldest_request))
            st.error(f"🛑 Rate limit exceeded! Please wait {seconds_left} seconds before generating another resume.")
        else:
            # log successful click timestamp
            st.session_state["request_timestamps"].append(current_time)
            
# Trigger
if st.button("Generate Tailored Resume", type="primary"):
    if not job_description:
        st.warning("Please provide a job description to initiate the optimization process.")
    else:
        with st.spinner("Claude is analyzing requirements and rewriting keywords..."):
            try:
                # System instructions for preventing AI hallucinations
                prompt_content = f"""
                You are an expert technical resume writer. Your task is to customize the provided Master Resume to align perfectly with the target Job Description.
                
                Guidelines:
                1. Do not invent false experience, tools, metrics, or certifications.
                2. Dynamically prioritize and highlight the skills, tools, and technical competencies listed in the Master Resume that map directly to the target responsibilities.
                3. Rewrite bullet points to mirror the professional vocabulary and action verbs used in the job description while maintaining the truth of the original metrics.
                4. Make resume universally ATS-friendly by ensuring all formatting is simple and consistent, and that keywords are naturally integrated.
                5. Make candidate as appealing as possible.
                6. Output ONLY the beautifully formatted markdown of the new resume. Do not include any chat commentary or conversational padding.
                
                Target Job Title: {job_title}
                
                Target Job Description:
                {job_description}
                
                Master Resume Base:
                {MASTER_RESUME}
                """

                # Call Claude
                message = client.messages.create(
                    model="claude-sonnet-4-6",
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
                
                # Add download option for markdown text file
                st.download_button(
                    label="Download Markdown File",
                    data=customized_resume,
                    file_name=f"Resume_{job_title.replace(' ', '_') if job_title else 'Tailored'}.md",
                    mime="text/markdown"
                )

            except Exception as e:
                 st.error(f"An infrastructure error occurred during generation: {e}")