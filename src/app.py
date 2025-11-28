import streamlit as st
from typing import Dict, Any, List
import os
import sys
import time
# Ensure the src directory is in the Python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
from inference_with_gemini import run_rag_for_query

st.set_page_config(page_title="Swift Visa Evaluator", page_icon="🛂", layout="wide")

# ============================
#     STYLES & BACKGROUND
# ============================
st.markdown("""
<style>
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    /* Apply the animated gradient to a fixed pseudo-element for smooth scrolling */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1;
        background: linear-gradient(-45deg, #a1c4fd, #ffc3a0);
        background-size: 400% 400%;
        will-change: background-position; /* Optimization for smooth animation */
        animation: gradient 15s ease infinite;
    }
    .stApp {
        background-color: transparent; /* Make the main app container transparent */
    }
    .card {
        padding: 20px;
        border-radius: 12px;
        background-color: #f8f9fa;
        border: 1px solid #e6e6e6;
        margin-top: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .success-card {
        background-color: #e1f7e9;
        border-left: 5px solid #28a745;
    }
    .title-center {
        text-align: center;
        font-size: 48px;
        font-weight: bold;
        padding: 20px;
        color: #333;
        text-shadow: 
            -1.5px -1.5px 0 #fff,  
             1.5px -1.5px 0 #fff,
            -1.5px  1.5px 0 #fff,
             1.5px  1.5px 0 #fff;
    }
    /* Style for input boxes */
    div[data-testid="stTextInput"] > div > div > input,
    div[data-testid="stNumberInput"] > div > div > input,
    div[data-testid="stTextArea"] > div > textarea,
    div[data-testid="stSelectbox"] > div {
        background-color: #ffffff;
        border: 1px solid #ccc;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        transition: border-color 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
    }

    /* Style for focused input boxes */
    div[data-testid="stTextInput"] > div > div > input:focus,
    div[data-testid="stNumberInput"] > div > div > input:focus,
    div[data-testid="stTextArea"] > div > textarea:focus,
    div[data-testid="stSelectbox"] > div:focus-within {
        border-color: #a1c4fd; /* Blue from gradient */
        box-shadow: 0 0 0 3px rgba(161, 196, 253, 0.4); /* Glow effect */
    }

    /* Floating help button */
    #help-toggle {
        display: none;
    }
    .floating-help-btn {
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 60px;
        height: 60px;
        background-color: #28a745; /* Green */
        color: white;
        border-radius: 50%;
        text-align: center;
        font-size: 30px;
        line-height: 60px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
        cursor: pointer;
        z-index: 999;
    }
    /* Modal styles */
    .help-modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.6);
        display: none;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    }
    .help-modal-content {
        background: #fff;
        color: #333;
        padding: 25px;
        border-radius: 10px;
        width: 90%;
        max-width: 450px;
        position: relative;
    }
    .help-modal-close {
        position: absolute;
        top: 10px;
        right: 15px;
        font-size: 28px;
        font-weight: bold;
        color: #888;
        text-decoration: none;
    }
    #help-toggle:checked ~ .help-modal-overlay {
        display: flex;
    }
    .contact-details p {
        margin: 10px 0;
        font-size: 16px;
    }

    /* New styles for result card */
    .result-card {
        position: relative; /* Needed for the animated border */
        background-color: #ffffff; /* White background for readability */
        border: 3px solid transparent; /* Make space for the gradient border */
        border-radius: 10px;
        padding: 25px;
        margin-top: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        background-clip: padding-box; /* Important: keeps background within padding */
    }
    .result-card::before {
        content: '';
        position: absolute;
        inset: 0;
        border-radius: inherit;
        padding: 3px; /* Border width */
        background: linear-gradient(-45deg, #a1c4fd, #ffc3a0);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        -webkit-mask: 
            linear-gradient(#fff 0 0) content-box, 
            linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
        z-index: -1;
    }
    .result-card .decision-line {
        font-size: 1.1em;
        color: #333;
        margin-bottom: 15px;
    }
    .result-card .explanation-text {
        color: #555;
        line-height: 1.6;
    }
    .confidence-high {
        color: #28a745;
        font-weight: bold;
    }
    .confidence-medium {
        color: #ffc107;
        font-weight: bold;
    }
    .confidence-low {
        color: #dc3545;
        font-weight: bold;
    }
    .section-title {
        font-size: 28px;
        font-weight: bold;
        color: #333;
        text-shadow: 
            -1px -1px 0 #fff,  
             1px -1px 0 #fff,
            -1px  1px 0 #fff,
             1px  1px 0 #fff;
    }

    /* New Footer Styles */
    .footer {
        background-color: #232f3e;
        color: #ddd;
        padding: 40px 20px;
        margin-top: 50px;
        font-size: 14px;
    }
    .footer-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        max-width: 1200px;
        margin: auto;
    }
    .footer-col h4 {
        color: #fff;
        margin-bottom: 15px;
        font-weight: bold;
    }
    .footer-col p, .footer-col a {
        color: #ccc;
        text-decoration: none;
        margin-bottom: 8px;
    }
    .footer-col a:hover {
        text-decoration: underline;
        color: #fff;
    }
</style>
""", unsafe_allow_html=True)

# ============================
#        HELP & SUPPORT
# ============================
st.markdown("""
    <input type="checkbox" id="help-toggle">
    <label for="help-toggle" class="floating-help-btn">💬</label>
    <div class="help-modal-overlay">
        <div class="help-modal-content">
            <label for="help-toggle" class="help-modal-close">&times;</label>
            <h3>Contact & Support</h3>
            <div class="contact-details">
                <p><strong>Name:</strong> M.stephen Prakash</p>
                <p><strong>Mobile:</strong> 7013428608</p>
                <p><strong>Email:</strong> <a href="mailto:stephenprakashmyla06@gmail.com">stephenprakashmyla06@gmail.com</a></p>
                <p><strong>LinkedIn:</strong> <a href="https://www.linkedin.com/in/myla-stephen-prakash-7166a7338" target="_blank">View Profile</a></p>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# ============================
#    CORE HELPER FUNCTIONS
# ============================

def get_confidence_class(confidence: int) -> str:
    """Returns a CSS class based on the confidence score."""
    if confidence >= 70:
        return "confidence-high"
    elif confidence >= 40:
        return "confidence-medium"
    else:
        return "confidence-low"


def get_category(visa_type: str) -> str:
    vt = visa_type.lower() if visa_type else ""
    if "f1" in vt or "student" in vt: return "f1"
    if "h1" in vt or "work" in vt: return "h1"
    if "b1" in vt or "b2" in vt or "tourist" in vt: return "b1b2"
    if "k1" in vt or "fiance" in vt: return "k1"
    return "other"


def merge_extra(user_profile: Dict[str, Any], category: str, additions: Dict[str, Any]):
    user_profile.setdefault("extra", {})
    user_profile["extra"].setdefault(category, {})
    user_profile["extra"][category].update(additions)


# ============================
#    RENDER VISA EXTRA FIELDS
# ============================

def render_visa_specific_inputs(category: str, extra: Dict[str, Any]):
    extra.setdefault(category, {})
    st.session_state.setdefault('extra', {}).setdefault(category, {})

    st.markdown("### Visa-Specific Information")

    c1, c2 = st.columns(2)

    if category == "f1":
        with c1:
            extra[category]["university_acceptance"] = st.selectbox(
                "University Acceptance?", ["Yes", "No", "Unknown"],
                index=["Yes","No","Unknown"].index(extra[category].get("university_acceptance", "Unknown"))
            )
            st.session_state['extra'][category]['university_acceptance'] = extra[category]["university_acceptance"]
            extra[category]["i20_issued"] = st.selectbox(
                "Is Form I-20 issued?",
                ["Yes", "No", "Unknown"],
                index=["Yes","No","Unknown"].index(extra[category].get("i20_issued", "Unknown"))
            )
            st.session_state['extra'][category]['i20_issued'] = extra[category]["i20_issued"]
        with c2:
            extra[category]["school_name"] = st.text_input(
                "School / University Name",
                value=extra[category].get("school_name", "")
            )
            st.session_state['extra'][category]['school_name'] = extra[category]["school_name"]
            extra[category]["proof_of_funds_amount"] = st.text_input(
                "Proof of Funds (Amount + Currency)",
                value=extra[category].get("proof_of_funds_amount", "")
            )
            st.session_state['extra'][category]['proof_of_funds_amount'] = extra[category]["proof_of_funds_amount"]
        extra[category]["test_scores"] = st.text_input(
            "Test Scores (TOEFL/IELTS/etc)",
            value=extra[category].get("test_scores", "")
        )
        st.session_state['extra'][category]['test_scores'] = extra[category]["test_scores"]

    elif category == "h1":
        with c1:
            extra[category]["job_offer"] = st.selectbox(
                "Job Offer Available?", ["Yes", "No"]
            )
            extra[category]["years_experience"] = st.number_input(
                "Years of Experience", min_value=0, value=0
            )
            st.session_state['extra'][category]['job_offer'] = extra[category]["job_offer"]
            st.session_state['extra'][category]['years_experience'] = extra[category]["years_experience"]
        with c2:
            extra[category]["employer_name"] = st.text_input(
                "Employer Name",
                value=extra[category].get("employer_name", "")
            )
            st.session_state['extra'][category]['employer_name'] = extra[category]["employer_name"]
            extra[category]["degree_equiv"] = st.selectbox(
                "Degree Equivalent to US Bachelor's?",
                ["Yes", "No", "Unknown"]
            )
            st.session_state['extra'][category]['degree_equiv'] = extra[category]["degree_equiv"]

    elif category == "b1b2":
        with c1:
            extra[category]["travel_purpose"] = st.selectbox(
                "Purpose of Travel", ["business", "tourism", "medical"]
            )
            extra[category]["return_ticket"] = st.selectbox(
                "Return Ticket Booked?", ["Yes", "No"]
            )
            st.session_state['extra'][category]['travel_purpose'] = extra[category]["travel_purpose"]
            st.session_state['extra'][category]['return_ticket'] = extra[category]["return_ticket"]
        with c2:
            extra[category]["trip_duration_days"] = st.number_input(
                "Trip Duration (days)", min_value=1, value=7
            )
            st.session_state['extra'][category]['trip_duration_days'] = extra[category]["trip_duration_days"]
            extra[category]["invitation_host"] = st.text_input(
                "Invitation / Host",
                value=extra[category].get("invitation_host", "")
            )
            st.session_state['extra'][category]['invitation_host'] = extra[category]["invitation_host"]

    elif category == "k1":
        with c1:
            extra[category]["us_citizen_sponsor"] = st.selectbox(
                "US Citizen Sponsor?", ["Yes", "No"]
            )
            extra[category]["relationship_length_months"] = st.number_input(
                "Relationship Length (months)", min_value=0, value=0
            )
            st.session_state['extra'][category]['us_citizen_sponsor'] = extra[category]["us_citizen_sponsor"]
            st.session_state['extra'][category]['relationship_length_months'] = extra[category]["relationship_length_months"]
        with c2:
            extra[category]["met_in_person"] = st.selectbox("Met in Person?", ["Yes", "No"])
            st.session_state['extra'][category]['met_in_person'] = extra[category]["met_in_person"]
            extra[category]["evidence_list"] = st.text_area(
                "Evidence (Photos, Tickets, Messages)",
                value=extra[category].get("evidence_list", "")
            )
            st.session_state['extra'][category]['evidence_list'] = extra[category]["evidence_list"]
    else:
        st.info("No extra fields needed for this visa type.")


# ============================
#        MAIN UI
# ============================

st.markdown('<div class="title-center">Swift Visa Eligibility Evaluator</div>', unsafe_allow_html=True)
st.markdown(
    "<p style='text-align: center; font-size: 18px; color: #333;'>🛂 Your fast track to understanding US visa requirements. Fill out the form below to get an instant eligibility evaluation based on official guidelines. Let's get started! 🚀</p>",
    unsafe_allow_html=True
)

# ============================
#    INPUT CALLBACKS (TOASTS)
# ============================
def show_toast(key, message):
    """Generic function to show a toast if the widget's value is not empty."""
    value = st.session_state.get(key)
    if value:
        st.toast(message.format(value=value))

def show_name_toast(): show_toast("user_name", "Hi {value}! 👋")
def show_age_toast(): show_toast("user_age", "Age {value}, got it!")
def show_nationality_toast(): show_toast("user_nationality", "{value}, a beautiful country!")
def show_education_toast(): show_toast("user_education", "Education in {value} is impressive!")
def show_employment_toast(): show_toast("user_employment", "Working as a {value} is great experience.")
def show_income_toast(): show_toast("user_income", "Financial details noted. 📝")

# Visa-specific toasts
def show_f1_uni_toast(): show_toast("f1_school_name", "Applying to {value}, exciting!")
def show_h1_employer_toast(): show_toast("h1_employer_name", "A job at {value} sounds great!")
def show_b1b2_host_toast(): show_toast("b1b2_invitation_host", "A visit with {value} is planned.")
def show_k1_evidence_toast(): show_toast("k1_evidence_list", "Evidence details recorded. ✅")
def show_passport_toast():
    status = st.session_state.get("user_passport_status")
    if status == "No":
        st.warning("A valid passport is required for all visa applications. Please apply for one before proceeding.")
    elif status == "Yes":
        st.toast("Great! Passport details are important. 👍")


        
st.markdown("---")

# Session states
for key, default in {
    "form_submitted": False,
    "final_result": None,
    "user_profile_state": None
}.items():
    st.session_state.setdefault(key, default)

visa_type_options = ["F1 Student", "H1B Work", "B1/B2 Visitor", "K1 Fiance", "Other"]
selected_visa_type = st.selectbox("Select Visa Type", visa_type_options)
category = get_category(selected_visa_type)

# =====================================
#           MAIN 2-COLUMN FORM
# =====================================

name = st.text_input("Full Name", key="user_name", on_change=show_name_toast)

c1, c2 = st.columns([3, 1])
with c1:
    passport_status = st.selectbox(
        "Do you have a valid passport?",
        ["", "Yes", "No"],
        key="user_passport_status",
        on_change=show_passport_toast
    )
    if passport_status == "Yes":
        passport_number = st.text_input("Passport Number", key="user_passport_number")

c1, c2 = st.columns([3, 1])
with c1:
    age = st.text_input("Age", key="user_age", on_change=show_age_toast)

left, right = st.columns(2)
with left:
    nationality = st.text_input("Nationality", key="user_nationality", on_change=show_nationality_toast)
    education = st.text_input("Education", key="user_education", on_change=show_education_toast)
with right:
    employment = st.text_input("Employment", key="user_employment", on_change=show_employment_toast)
    income = st.text_input("Income", key="user_income", on_change=show_income_toast)

st.markdown("---")

with st.form(key="visa_form"):
    # Visa-specific inputs remain in the form
    temp_extra = {}
    render_visa_specific_inputs(category, temp_extra)

    submitted = st.form_submit_button("Evaluate Visa Eligibility")

# =========================================
#       FIRST EVALUATION WITH SPINNER
# =========================================
if submitted:
    # Collect values from session state for widgets outside the form
    name_val = st.session_state.get("user_name", "")
    age_val = st.session_state.get("user_age", "")
    nationality_val = st.session_state.get("user_nationality", "")
    education_val = st.session_state.get("user_education", "")
    employment_val = st.session_state.get("user_employment", "")
    income_val = st.session_state.get("user_income", "")
    passport_status_val = st.session_state.get("user_passport_status", "")
    passport_number_val = st.session_state.get("user_passport_number", "")

    st.session_state.form_submitted = True

    user_profile = {
        "name": name_val, "age": age_val, "nationality": nationality_val,
        "passport_status": passport_status_val,
        "passport_number": passport_number_val,
        "education": education_val, "employment": employment_val, "income": income_val,
        "visa_type": selected_visa_type,
        "extra": {}
    }

    merge_extra(user_profile, category, st.session_state.get('extra', {}).get(category, {}))

    with st.spinner("Evaluating your visa eligibility... Please wait..."):
        time.sleep(1.5)
        result = run_rag_for_query(user_profile, f"{selected_visa_type} requirements for {nationality_val}")
    
    st.session_state.user_profile_state = user_profile
    st.session_state.final_result = result


# =========================================
#          DISPLAY RESULTS SECTION
# =========================================
if st.session_state.form_submitted and st.session_state.final_result:
    result = st.session_state.final_result
    decision = result.get("decision", "Insufficient Data")
    explanation = result.get("explanation", "No explanation provided.")
    confidence = result.get("confidence", 0)
    missing = result.get("missing_information") or []

    st.markdown("---")
    st.markdown('<div class="section-title">🧾 Evaluation Result</div>', unsafe_allow_html=True)

    confidence_class = get_confidence_class(confidence)
    
    # Personalize the explanation by replacing "user" with the applicant's name
    applicant_name = st.session_state.user_profile_state.get("name", "The applicant")
    if applicant_name:
        explanation = explanation.replace("user", applicant_name).replace("User", applicant_name)

    result_html = f"""
    <div class="result-card">
        <div class="decision-line">
            <strong>Decision:</strong> {decision} | <strong>Confidence:</strong> <span class="{confidence_class}">{confidence}%</span>
        </div>
        <hr>
        <p class="explanation-text">{explanation.replace('the applicant', applicant_name, 1).capitalize()}</p>
    </div>
    """
    st.markdown(result_html, unsafe_allow_html=True)

    # Missing info section
    if missing:
        with st.expander("Provide Missing Information", expanded=True):
            missing_inputs = {}
            c1, c2 = st.columns(2)

            for i, key in enumerate(missing):
                col = c1 if i % 2 == 0 else c2

                with col:
                    if "." in key:
                        cat, k = key.split(".", 1)
                    else:
                        cat = category
                        k = key

                    label = k.replace("_", " ").capitalize()
                    missing_inputs.setdefault(cat, {})

                    if k in ["university_acceptance", "i20_issued", "degree_equiv"]:
                        missing_inputs[cat][k] = st.selectbox(label, ["Yes", "No", "Unknown"])
                    elif k in ["job_offer", "return_ticket", "us_citizen_sponsor", "met_in_person"]:
                        missing_inputs[cat][k] = st.selectbox(label, ["Yes", "No"])
                    elif k in ["trip_duration_days", "years_experience", "relationship_length_months"]:
                        missing_inputs[cat][k] = st.number_input(label, min_value=0, step=1)
                    else:
                        missing_inputs[cat][k] = st.text_input(label)

            col1, col2 = st.columns(2)
            submit_missing = col1.button("Submit Missing Info")
            cancel = col2.button("Cancel")

            if submit_missing:
                for c, fields in missing_inputs.items():
                    merge_extra(st.session_state.user_profile_state, c, fields)

                with st.spinner("Re-evaluating with additional information..."):
                    time.sleep(1.2)
                    result2 = run_rag_for_query(
                        st.session_state.user_profile_state,
                        # Use the nationality from the stored user profile
                        f"{selected_visa_type} requirements for {st.session_state.user_profile_state.get('nationality', '')}"
                    )

                st.session_state.final_result = result2
                st.rerun()

            elif cancel:
                st.info("Evaluation cancelled.")

    # Add a button to start a new evaluation
    st.markdown("---")
    if st.button("Re-evaluate from Start", use_container_width=True):
        # Clear all session state to reset the app
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ======================
#  FOOTER
# ======================
st.markdown(
    """
    <div class="footer">
        <div class="footer-container">
            <div class="footer-col">
                <h4>Resources</h4>
                <a href="#">Official Visa Website</a>
                <a href="#">Policy Documents</a>
                <a href="#">FAQs</a>
            </div>
            <div class="footer-col">
                <h4>Legal</h4>
                <p>This application is for pre-evaluation purposes only and is not a substitute for official immigration advice. The eligibility decision is not a guarantee of a real visa outcome.</p>
            </div>
            <div class="footer-col">
                <h4>Disclaimer</h4>
                <p>Always consult with official immigration authorities for definitive guidance. The creators of this tool are not responsible for any visa application results.</p>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
