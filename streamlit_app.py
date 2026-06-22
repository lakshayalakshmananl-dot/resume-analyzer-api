import streamlit as st
import requests

# ── Config ────────────────────────────────────────────────
API_URL = "https://resume-analyzer-api-production-4a17.up.railway.app"

st.set_page_config(
    page_title="Critiqo",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Styling ───────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* { font-family: 'Inter', sans-serif; }

.stApp {
    background-color: #0a0a0f;
    color: #e8e8e8;
}

section[data-testid="stSidebar"] {
    background-color: #0f0f17;
    border-right: 1px solid #1e1e2e;
}

.critiqo-header {
    text-align: center;
    padding: 2rem 0 1rem 0;
}

.critiqo-logo {
    font-size: 3rem;
    font-weight: 700;
    background: linear-gradient(135deg, #f5a623, #f76b1c);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -1px;
}

.critiqo-tagline {
    color: #888;
    font-size: 1rem;
    font-weight: 300;
    margin-top: 0.3rem;
}

.card {
    background: #13131f;
    border: 1px solid #1e1e2e;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

.score-circle {
    text-align: center;
    padding: 2rem;
}

.score-number {
    font-size: 5rem;
    font-weight: 700;
    line-height: 1;
}

.score-label {
    font-size: 0.9rem;
    color: #888;
    margin-top: 0.5rem;
}

.skill-tag {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 500;
    margin: 3px;
}

.skill-match {
    background: #0d2b1a;
    color: #4ade80;
    border: 1px solid #166534;
}

.skill-missing {
    background: #2b0d0d;
    color: #f87171;
    border: 1px solid #991b1b;
}

.suggestion-item {
    background: #0d1a2b;
    border-left: 3px solid #f5a623;
    padding: 0.75rem 1rem;
    border-radius: 0 8px 8px 0;
    margin-bottom: 0.5rem;
    color: #ccc;
    font-size: 0.9rem;
}

.stTextInput > div > div > input {
    background-color: #13131f !important;
    border: 1px solid #2a2a3e !important;
    color: #e8e8e8 !important;
    border-radius: 8px !important;
}

.stTextInput > div > div > input:focus {
    border-color: #f5a623 !important;
    box-shadow: 0 0 0 1px #f5a623 !important;
}

.stTextArea > div > div > textarea {
    background-color: #13131f !important;
    border: 1px solid #2a2a3e !important;
    color: #e8e8e8 !important;
    border-radius: 8px !important;
}

div[data-testid="stFileUploader"] {
    background-color: #13131f !important;
    border: 2px dashed #2a2a3e !important;
    border-radius: 12px !important;
}

.stButton > button {
    background: linear-gradient(135deg, #f5a623, #f76b1c) !important;
    color: #000 !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.5rem 2rem !important;
    font-size: 0.95rem !important;
    width: 100% !important;
    transition: opacity 0.2s !important;
}

.stButton > button:hover {
    opacity: 0.85 !important;
}

.success-msg {
    background: #0d2b1a;
    border: 1px solid #166534;
    color: #4ade80;
    padding: 0.75rem 1rem;
    border-radius: 8px;
    font-size: 0.9rem;
    margin-bottom: 1rem;
}

.error-msg {
    background: #2b0d0d;
    border: 1px solid #991b1b;
    color: #f87171;
    padding: 0.75rem 1rem;
    border-radius: 8px;
    font-size: 0.9rem;
    margin-bottom: 1rem;
}

.info-msg {
    background: #0d1a2b;
    border: 1px solid #1e3a5f;
    color: #93c5fd;
    padding: 0.75rem 1rem;
    border-radius: 8px;
    font-size: 0.9rem;
    margin-bottom: 1rem;
}

.extracted-text {
    background: #13131f;
    border: 1px solid #2a2a3e;
    border-radius: 8px;
    padding: 1rem;
    color: #e8e8e8;
    font-size: 0.85rem;
    line-height: 1.6;
    max-height: 200px;
    overflow-y: auto;
    white-space: pre-wrap;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "auth"
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "uploaded_resume" not in st.session_state:
    st.session_state.uploaded_resume = None
if "nav" not in st.session_state:
    st.session_state.nav = "Upload Resume"
if "just_uploaded" not in st.session_state:
    st.session_state.just_uploaded = False

# ── API Helpers ───────────────────────────────────────────
def auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}

def api_post(endpoint, data=None, files=None, form=False):
    try:
        headers = auth_headers() if st.session_state.token else {}
        if form:
            r = requests.post(f"{API_URL}{endpoint}", data=data, headers=headers, timeout=60)
        elif files:
            r = requests.post(f"{API_URL}{endpoint}", files=files, headers=headers, timeout=60)
        else:
            r = requests.post(f"{API_URL}{endpoint}", json=data, headers=headers, timeout=60)
        return r
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None

def api_get(endpoint):
    try:
        r = requests.get(f"{API_URL}{endpoint}", headers=auth_headers(), timeout=30)
        return r
    except:
        return None

# ── Score Color ───────────────────────────────────────────
def score_color(score):
    if score >= 75:
        return "#4ade80"
    elif score >= 50:
        return "#f5a623"
    else:
        return "#f87171"

# ── Header ────────────────────────────────────────────────
def render_header():
    st.markdown("""
    <div class="critiqo-header">
        <div class="critiqo-logo">⚡ Critiqo</div>
        <div class="critiqo-tagline">AI-powered resume intelligence</div>
    </div>
    """, unsafe_allow_html=True)

# ── Auth Page ─────────────────────────────────────────────
def auth_page():
    render_header()
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        tab1, tab2 = st.tabs(["Sign In", "Create Account"])

        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            email = st.text_input("Email", placeholder="yourname@gmail.com", key="login_email")
            password = st.text_input("Password", type="password", placeholder="••••••••", key="login_pass")
            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("Sign In", key="login_btn"):
                if email and password:
                    with st.spinner("Authenticating..."):
                        r = api_post("/users/login", data={"username": email, "password": password}, form=True)
                    if r and r.status_code == 200:
                        st.session_state.token = r.json()["access_token"]
                        me = api_get("/users/me")
                        if me:
                            st.session_state.user = me.json()
                        st.session_state.page = "dashboard"
                        st.session_state.nav = "Upload Resume"
                        st.rerun()
                    else:
                        st.markdown('<div class="error-msg">Invalid email or password.</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="error-msg">Please fill in all fields.</div>', unsafe_allow_html=True)

        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            reg_email = st.text_input("Email", placeholder="yourname@gmail.com", key="reg_email")
            reg_username = st.text_input("Username", placeholder="johndoe", key="reg_username")
            reg_password = st.text_input("Password", type="password", placeholder="Min 6 characters", key="reg_pass")
            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("Create Account", key="reg_btn"):
                if reg_email and reg_username and reg_password:
                    with st.spinner("Creating account..."):
                        r = api_post("/users/register", data={
                            "email": reg_email,
                            "username": reg_username,
                            "password": reg_password
                        })
                    if r and r.status_code == 201:
                        st.markdown('<div class="success-msg">Account created! Please sign in.</div>', unsafe_allow_html=True)
                    elif r and r.status_code == 400:
                        st.markdown(f'<div class="error-msg">{r.json()["detail"]}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="error-msg">Something went wrong. Try again.</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="error-msg">Please fill in all fields.</div>', unsafe_allow_html=True)

# ── Dashboard ─────────────────────────────────────────────
def dashboard_page():
    with st.sidebar:
        st.markdown(f"""
        <div style="padding: 1rem 0;">
            <div style="font-size: 1.3rem; font-weight: 700; color: #f5a623;">⚡ Critiqo</div>
            <div style="font-size: 0.8rem; color: #888; margin-top: 0.2rem;">AI Resume Intelligence</div>
        </div>
        <hr style="border-color: #1e1e2e;">
        """, unsafe_allow_html=True)

        if st.session_state.user:
            st.markdown(f"""
            <div style="padding: 0.5rem 0; margin-bottom: 1rem;">
                <div style="font-size: 0.75rem; color: #888;">Signed in as</div>
                <div style="font-size: 0.9rem; color: #e8e8e8; font-weight: 500;">{st.session_state.user.get('email', '')}</div>
            </div>
            """, unsafe_allow_html=True)

        nav = st.radio(
            "",
            ["Upload Resume", "Analyze", "My Resumes", "My Analyses"],
            label_visibility="collapsed",
            index=["Upload Resume", "Analyze", "My Resumes", "My Analyses"].index(st.session_state.nav)
        )
        st.session_state.nav = nav

        st.markdown("<br>" * 5, unsafe_allow_html=True)
        if st.button("Sign Out"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    if nav == "Upload Resume":
        upload_page()
    elif nav == "Analyze":
        analyze_page()
    elif nav == "My Resumes":
        my_resumes_page()
    elif nav == "My Analyses":
        my_analyses_page()

# ── Upload Page ───────────────────────────────────────────
def upload_page():
    st.markdown("## Upload Resume")
    st.markdown('<div class="critiqo-tagline">Upload your PDF resume to get started</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        uploaded_file = st.file_uploader("Drop your resume here", type=["pdf"], help="Only PDF files are supported")

        if not uploaded_file:
            st.session_state.just_uploaded = False

        if uploaded_file:
            st.markdown(f'<div class="info-msg">📄 {uploaded_file.name} selected ({round(uploaded_file.size/1024, 1)} KB)</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("Upload & Extract Text"):
                with st.spinner("Uploading and extracting text..."):
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                    r = api_post("/resumes/upload", files=files)

                if r and r.status_code == 200:
                    data = r.json()
                    st.session_state.uploaded_resume = data
                    st.session_state.just_uploaded = True
                    st.rerun()
                else:
                    st.markdown('<div class="error-msg">Upload failed. Please try again.</div>', unsafe_allow_html=True)

            # Fixed: Render content outside of the conditional trigger block
            if st.session_state.just_uploaded and st.session_state.uploaded_resume:
                st.markdown('<div class="success-msg">✅ Resume uploaded successfully!</div>', unsafe_allow_html=True)

                extracted = st.session_state.uploaded_resume.get("extracted_text", "")
                if extracted:
                    st.markdown("**Extracted Text Preview:**")
                    st.markdown(f'<div class="extracted-text">{extracted[:1000]}{"..." if len(extracted) > 1000 else ""}</div>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown('<div class="success-msg">✅ Ready! Click "Analyze" in the sidebar to score your resume.</div>', unsafe_allow_html=True)

                # Safe explicit callback to update layout state instantly
                def go_to_analyze():
                    st.session_state.nav = "Analyze"
                    st.session_state.just_uploaded = False

                st.button("Go to Analyze →", on_click=go_to_analyze)

    with col2:
        st.markdown("""
        <div class="card">
            <div style="font-size: 0.85rem; color: #888; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 1rem;">Tips</div>
            <div style="font-size: 0.85rem; color: #ccc; line-height: 1.8;">
                ✦ Use a text-based PDF<br>
                ✦ Avoid scanned images<br>
                ✦ Keep it under 5MB<br>
                ✦ One resume per analysis
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.uploaded_resume:
            st.markdown(f"""
            <div class="card">
                <div style="font-size: 0.75rem; color: #888; text-transform: uppercase; letter-spacing: 1px;">Last Uploaded</div>
                <div style="font-size: 0.9rem; color: #f5a623; margin-top: 0.5rem;">📄 {st.session_state.uploaded_resume['filename']}</div>
            </div>
            """, unsafe_allow_html=True)

# ── Analyze Page ──────────────────────────────────────────
def analyze_page():
    st.markdown("## Analyze Resume")
    st.markdown('<div class="critiqo-tagline">Match your resume against a job description</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    r = api_get("/resumes/?limit=50")
    if not r or r.status_code != 200:
        st.markdown('<div class="error-msg">Could not fetch resumes. Please upload one first.</div>', unsafe_allow_html=True)
        return

    resumes = r.json().get("items", [])
    if not resumes:
        st.markdown('<div class="info-msg">No resumes found. Please upload a resume first.</div>', unsafe_allow_html=True)
        if st.button("Upload Resume"):
            st.session_state.nav = "Upload Resume"
            st.rerun()
        return

    col1, col2 = st.columns([1.5, 1])
    with col1:
        resume_options = {res["filename"]: res["id"] for res in resumes}

        default_idx = 0
        if st.session_state.uploaded_resume:
            names = list(resume_options.keys())
            last_name = st.session_state.uploaded_resume.get("filename", "")
            if last_name in names:
                default_idx = names.index(last_name)

        selected_resume = st.selectbox("Select Resume", list(resume_options.keys()), index=default_idx)
        resume_id = resume_options[selected_resume]

        job_title = st.text_input("Job Title", placeholder="e.g. Backend Developer, Data Scientist")
        job_description = st.text_area(
            "Job Description",
            placeholder="Paste the full job description here...\n\nExample: We are looking for a Python backend developer with experience in FastAPI, PostgreSQL, REST APIs...",
            height=220
        )

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("⚡ Analyze Now"):
            if not job_description or len(job_description) < 10:
                st.markdown('<div class="error-msg">Job description must be at least 10 characters.</div>', unsafe_allow_html=True)
            else:
                with st.spinner("AI is analyzing your resume... this may take 10-15 seconds"):
                    r = api_post("/analyses/", data={
                        "resume_id": resume_id,
                        "job_description": job_description,
                        "job_title": job_title
                    })

                if r and r.status_code == 200:
                    st.session_state.analysis_result = r.json()
                    st.rerun()
                else:
                    st.markdown('<div class="error-msg">Analysis failed. Please try again.</div>', unsafe_allow_html=True)

    with col2:
        if st.session_state.analysis_result:
            result = st.session_state.analysis_result
            score = result.get("score", 0)
            color = score_color(score)

            st.markdown(f"""
            <div class="card score-circle">
                <div class="score-number" style="color: {color};">{score}</div>
                <div class="score-label">Match Score / 100</div>
            </div>
            """, unsafe_allow_html=True)

            matched = result.get("matched_skills", [])
            missing = result.get("missing_skills", [])

            if matched:
                st.markdown("**✅ Matched Skills**")
                tags = " ".join([f'<span class="skill-tag skill-match">{s}</span>' for s in matched])
                st.markdown(f'<div style="margin-bottom:1rem;">{tags}</div>', unsafe_allow_html=True)

            if missing:
                st.markdown("**❌ Missing Skills**")
                tags = " ".join([f'<span class="skill-tag skill-missing">{s}</span>' for s in missing])
                st.markdown(f'<div style="margin-bottom:1rem;">{tags}</div>', unsafe_allow_html=True)

            suggestions = result.get("suggestions", [])
            if suggestions:
                st.markdown("**💡 Suggestions**")
                for s in suggestions:
                    st.markdown(f'<div class="suggestion-item">→ {s}</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="card" style="text-align:center; padding: 3rem 1.5rem;">
                <div style="font-size: 2.5rem; margin-bottom: 1rem;">⚡</div>
                <div style="color: #888; font-size: 0.9rem;">Your analysis results will appear here after you click Analyze Now</div>
            </div>
            """, unsafe_allow_html=True)

# ── My Resumes Page ───────────────────────────────────────
def my_resumes_page():
    st.markdown("## My Resumes")
    st.markdown("<br>", unsafe_allow_html=True)

    r = api_get("/resumes/?limit=50")
    if not r or r.status_code != 200:
        st.markdown('<div class="error-msg">Could not fetch resumes.</div>', unsafe_allow_html=True)
        return

    data = r.json()
    resumes = data.get("items", [])
    total = data.get("total", 0)

    st.markdown(f'<div style="color: #888; font-size: 0.85rem; margin-bottom: 1rem;">{total} resume(s) uploaded</div>', unsafe_allow_html=True)

    if not resumes:
        st.markdown('<div class="info-msg">No resumes yet. Upload one to get started.</div>', unsafe_allow_html=True)
        return

    for res in resumes:
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            st.markdown(f"**📄 {res['filename']}**")
        with col2:
            st.markdown(f"<span style='color: #888; font-size: 0.85rem;'>Uploaded {res['upload_date'][:10]}</span>", unsafe_allow_html=True)
        with col3:
            if st.button("Delete", key=f"del_res_{res['id']}"):
                rd = requests.delete(f"{API_URL}/resumes/{res['id']}", headers=auth_headers())
                if rd.status_code == 204:
                    st.rerun()
        st.markdown("<hr style='border-color: #1e1e2e; margin: 0.5rem 0;'>", unsafe_allow_html=True)

# ── My Analyses Page ──────────────────────────────────────
def my_analyses_page():
    st.markdown("## My Analyses")
    st.markdown("<br>", unsafe_allow_html=True)

    r = api_get("/analyses/?limit=50")
    if not r or r.status_code != 200:
        st.markdown('<div class="error-msg">Could not fetch analyses.</div>', unsafe_allow_html=True)
        return

    data = r.json()
    analyses = data.get("items", [])
    total = data.get("total", 0)

    st.markdown(f'<div style="color: #888; font-size: 0.85rem; margin-bottom: 1rem;">{total} analysis result(s)</div>', unsafe_allow_html=True)

    if not analyses:
        st.markdown('<div class="info-msg">No analyses yet. Run an analysis to see results here.</div>', unsafe_allow_html=True)
        return

    for analysis in analyses:
        score = analysis.get("score", 0)
        color = score_color(score)
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        with col1:
            st.markdown(f"**{analysis.get('job_title', 'Untitled')}**")
        with col2:
            st.markdown(f"<span style='color: {color}; font-weight: 700;'>{score}/100</span>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<span style='color: #888; font-size: 0.85rem;'>{analysis['created_at'][:10]}</span>", unsafe_allow_html=True)
        with col4:
            if st.button("Delete", key=f"del_an_{analysis['id']}"):
                rd = requests.delete(f"{API_URL}/analyses/{analysis['id']}", headers=auth_headers())
                if rd.status_code == 204:
                    st.rerun()
        st.markdown("<hr style='border-color: #1e1e2e; margin: 0.5rem 0;'>", unsafe_allow_html=True)

# ── Router ────────────────────────────────────────────────
if st.session_state.page == "auth":
    auth_page()
else:
    dashboard_page()