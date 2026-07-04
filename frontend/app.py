import streamlit as st
import requests

# =====================================================
# ================= PAGE CONFIG =======================
# =====================================================

st.set_page_config(
    page_title="AI Legal Assistant",
    layout="centered"
)

API_URL = "http://127.0.0.1:8002/analyze"

# =====================================================
# ================= CUSTOM CSS ========================
# =====================================================

st.markdown("""
<style>

.main {
    background-color: #0b1120;
}

h1, h2, h3 {
    font-weight: 800 !important;
}

.section-card {
    background-color: #111827;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #374151;
    margin-bottom: 20px;
}

.heading {
    font-size: 30px;
    font-weight: 900;
    color: white;
    margin-top: 35px;
    margin-bottom: 20px;
}

.subheading {
    font-size: 24px;
    font-weight: bold;
    color: #f59e0b;
}

.result-text {
    color: white;
    font-size: 17px;
    line-height: 1.8;
}

.step-box {
    background-color: #111827;
    padding: 15px;
    border-left: 5px solid #3b82f6;
    border-radius: 10px;
    margin-bottom: 10px;
    color: white;
}

.prob-box {
    background-color: #111827;
    padding: 15px;
    border-radius: 10px;
    border-left: 5px solid #10b981;
    margin-bottom: 12px;
    color: white;
}

.timeline-box {
    background-color: #111827;
    padding: 15px;
    border-radius: 10px;
    border-left: 5px solid #f59e0b;
    margin-bottom: 12px;
    color: white;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# ================= SESSION STATE =====================
# =====================================================

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# =====================================================
# ================= HEADER ============================
# =====================================================

st.title("⚖️ AI Legal Assistant")

role = st.selectbox(
    "Continue as",
    ["Citizen", "Lawyer"]
)

st.warning(
    "This system provides legal decision support only. "
    "Final responsibility lies with a qualified lawyer."
)

# =====================================================
# ================= DISPLAY CHAT ======================
# =====================================================

for message in st.session_state.chat_history:

    with st.chat_message(message["role"]):

        st.markdown(
            message["content"],
            unsafe_allow_html=True
        )

# =====================================================
# ================= USER INPUT ========================
# =====================================================

user_input = st.chat_input(
    "Describe your legal problem..."
)

if user_input:

    # =================================================
    # ================= USER MESSAGE ==================
    # =================================================

    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    # =================================================
    # ================= ASSISTANT =====================
    # =================================================

    with st.chat_message("assistant"):

        with st.spinner("Analyzing legal issue..."):

            try:

                response = requests.post(
                    API_URL,
                    json={
                        "text": user_input,
                        "role": role
                    },
                    timeout=120
                )

                result = response.json()

            except Exception:

                st.error(
                    "❌ Backend connection failed."
                )

                st.stop()

        # =================================================
        # ================= LEGAL DOMAIN ==================
        # =================================================

        if result.get("domain"):

            st.markdown(f"""
            <div class="section-card">

            <h2 class="subheading">
                LEGAL DOMAIN
            </h2>

            <p class="result-text">
                {result['domain'].title()}
            </p>

            </div>
            """, unsafe_allow_html=True)

        # =================================================
        # ================= IPC SECTIONS ==================
        # =================================================

        if result.get("ipc_sections"):

            st.markdown("""
            <div class="heading">
                RELEVANT IPC SECTIONS
            </div>
            """, unsafe_allow_html=True)

            for law in result["ipc_sections"]:

                st.markdown(f"""
                <div class="section-card">

                <h2 style="
                    color:#fbbf24;
                    font-weight:bold;
                ">
                    IPC SECTION
                    {law.get('section_or_article', '')}
                </h2>

                <h3 style="color:white;">
                    {law.get('title', '')}
                </h3>

                <p class="result-text">
                    <b>Punishment:</b>
                    {law.get('punishment', '')}
                </p>

                <p class="result-text">
                    <b>Cognizable:</b>
                    {law.get('cognizable', '')}
                </p>

                <p class="result-text">
                    <b>Bailable:</b>
                    {law.get('bailable', '')}
                </p>

                </div>
                """, unsafe_allow_html=True)

        # =================================================
        # ================= SIMILAR CASE LAWS =============
        # =================================================

        if result.get("case_laws"):

            st.markdown("""
            <div class="heading">
                SIMILAR CASE LAWS
            </div>
            """, unsafe_allow_html=True)

            for case in result["case_laws"]:

                title = case.get(
                    "title",
                    "Unknown Case"
                )

                summary = case.get(
                    "summary",
                    "No summary available."
                )

                verdict = case.get(
                    "verdict",
                    "Verdict unavailable."
                )

                source_link = case.get(
                    "source_link",
                    "#"
                )

                # ---------------- CLEAN TEXT ----------------

                summary = str(summary).strip()

                verdict = str(verdict).strip()

                remove_phrases = [

                    "Here is a summary of the verdict in 2-3 simple and clear lines:",

                    "Here is a summary of the legal verdict:",

                    "Here is a summary of the legal verdict in 2-3 simple and clear lines:",

                    "Here is a summary of the verdict:",

                    "Summary of verdict:"
                ]

                for phrase in remove_phrases:

                    verdict = verdict.replace(
                        phrase,
                        ""
                    )

                verdict = " ".join(
                    verdict.split()
                )

                summary = " ".join(
                    summary.split()
                )

                # ---------------- DISPLAY CARD ----------------

                st.markdown(f"""
                <div class="section-card">

                <h3 style="
                    color:#34d399;
                    font-weight:bold;
                    margin-bottom:15px;
                ">
                    ⚖️ {title}
                </h3>

                <p class="result-text">
                    <b>Case Summary:</b>
                    <br><br>
                    {summary}
                </p>

                <p class="result-text">
                    <b>Verdict:</b>
                    <br><br>
                    {verdict}
                </p>

                <a href="{source_link}"
                   target="_blank"
                   style="
                       color:#60a5fa;
                       font-weight:bold;
                       text-decoration:none;
                   ">

                   🔗 View Full Case

                </a>

                </div>
                """, unsafe_allow_html=True)

        # =================================================
        # ================= LEGAL ANALYSIS ================
        # =================================================

        if result.get("legal_analysis"):

            st.markdown("""
            <div class="heading">
                LEGAL ANALYSIS
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="section-card">

            <p class="result-text">
                {result['legal_analysis']}
            </p>

            </div>
            """, unsafe_allow_html=True)

        # =================================================
        # ================= SIMPLE EXPLANATION ============
        # =================================================

        if result.get("simple_explanation"):

            st.markdown("""
            <div class="heading">
                SIMPLE EXPLANATION
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="section-card">

            <p class="result-text">
                {result['simple_explanation']}
            </p>

            </div>
            """, unsafe_allow_html=True)

        # =================================================
        # ================= SEVERITY ======================
        # =================================================

        if result.get("severity_level"):

            st.markdown(f"""
            <div class="section-card">

            <h2 style="
                color:#ef4444;
                font-weight:bold;
            ">

            SEVERITY LEVEL:
            {result['severity_level']}

            </h2>

            </div>
            """, unsafe_allow_html=True)

        # =================================================
        # ================= NEXT STEPS ====================
        # =================================================

        if result.get("recommended_next_steps"):

            st.markdown("""
            <div class="heading">
                RECOMMENDED NEXT STEPS
            </div>
            """, unsafe_allow_html=True)

            for step in result[
                "recommended_next_steps"
            ]:

                st.markdown(f"""
                <div class="step-box">
                    {step}
                </div>
                """, unsafe_allow_html=True)

        # =================================================
        # ================= LAWYER FEATURES ===============
        # =================================================

        if role == "Lawyer":

            # ---------------- TIMELINE ----------------

            if result.get(
                "estimated_legal_timeline"
            ):

                st.markdown("""
                <div class="heading">
                    ESTIMATED LEGAL TIMELINE
                </div>
                """, unsafe_allow_html=True)

                timeline = result[
                    "estimated_legal_timeline"
                ]

                for stage, value in timeline.items():

                    st.markdown(f"""
                    <div class="timeline-box">

                    <p class="result-text">
                        <b>{stage}:</b> {value}
                    </p>

                    </div>
                    """, unsafe_allow_html=True)

            # ---------------- QUESTIONS ----------------

            if result.get(
                "cross_examination_questions"
            ):

                st.markdown("""
                <div class="heading">
                    CROSS EXAMINATION QUESTIONS
                </div>
                """, unsafe_allow_html=True)

                for question in result[
                    "cross_examination_questions"
                ]:

                    st.markdown(f"""
                    <div class="step-box">
                        {question}
                    </div>
                    """, unsafe_allow_html=True)

            # ---------------- DOCUMENT COMPARISON ----------------

            if result.get(
                "document_comparison"
            ):

                st.markdown("""
                <div class="heading">
                    DOCUMENT COMPARISON
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div class="section-card">

                <p class="result-text">
                    {result['document_comparison']}
                </p>

                </div>
                """, unsafe_allow_html=True)

            # ---------------- PROBABILITY ----------------

            if result.get(
                "legal_probability_prediction"
            ):

                st.markdown("""
                <div class="heading">
                    LEGAL PROBABILITY PREDICTION
                </div>
                """, unsafe_allow_html=True)

                probs = result[
                    "legal_probability_prediction"
                ]

                for key, value in probs.items():

                    st.markdown(f"""
                    <div class="prob-box">

                    <p class="result-text">
                        <b>{key}:</b> {value}
                    </p>

                    </div>
                    """, unsafe_allow_html=True)

        # =================================================
        # ================= SAVE CHAT =====================
        # =================================================

        st.session_state.chat_history.append({

            "role": "assistant",

            "content":
                "Legal analysis generated successfully."
        })