import streamlit as st
import json
import time

st.set_page_config(
    page_title="MindGraph AI - Enterprise Auth",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# DIRECT INJECTED CSS WITH HIGH PRIORITY OVERRIDES
# -----------------------------------------------------------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Plus+Jakarta+Sans:wght@300;400;600&display=swap');

    /* Global Dark Theme Force */
    html, body, .stApp {
        background: radial-gradient(circle at 50% 30%, #0f172a 0%, #030712 100%) !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* Hide Top Nav & Footers */
    header[data-testid="stHeader"], footer {
        visibility: hidden !important;
        display: none !important;
    }

    /* Streamlit Main Container Adjustment */
    .main .block-container {
        padding-top: 3rem !important;
        max-width: 1100px !important;
    }

    /* FORCE CYBERPUNK FORM CONTAINER */
    div[data-testid="stForm"] {
        background: rgba(15, 23, 42, 0.85) !important;
        border: 1px solid rgba(59, 130, 246, 0.4) !important;
        box-shadow: 0 0 45px rgba(37, 99, 235, 0.35), inset 0 0 20px rgba(59, 130, 246, 0.15) !important;
        border-radius: 24px !important;
        padding: 40px 30px !important;
    }

    /* Input Labels */
    div[data-testid="stForm"] label p {
        color: #60a5fa !important;
        font-weight: 700 !important;
        font-size: 11px !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase !important;
    }

    /* Input Fields Background & Border Override */
    div[data-baseweb="input"], div[data-baseweb="input"] input {
        background-color: rgba(30, 41, 59, 0.9) !important;
        color: #f8fafc !important;
        border-radius: 10px !important;
    }

    div[data-baseweb="input"] {
        border: 1px solid rgba(148, 163, 184, 0.3) !important;
    }

    div[data-baseweb="input"]:focus-within {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 18px rgba(59, 130, 246, 0.6) !important;
    }

    /* Submit Button styling */
    div[data-testid="stForm"] button[kind="secondaryFormSubmit"], 
    div[data-testid="stForm"] button {
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%) !important;
        color: #ffffff !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        letter-spacing: 1.5px !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px 20px !important;
        box-shadow: 0 4px 25px rgba(37, 99, 235, 0.5) !important;
        width: 100% !important;
        margin-top: 15px !important;
        transition: all 0.3s ease !important;
    }

    div[data-testid="stForm"] button:hover {
        box-shadow: 0 8px 35px rgba(124, 58, 237, 0.8) !important;
        transform: translateY(-2px) !important;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SESSION STATE
# -----------------------------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "db" not in st.session_state:
    st.session_state.db = [
        {
            "id": "KB-101",
            "decision": "Adopted PostgreSQL over MongoDB for Core User Data",
            "rationale": "Strong ACID compliance requirement for financial transactions.",
            "risks": "Requires complex manual scaling/sharding at higher traffic volumes.",
            "author": "alex_techlead"
        }
    ]

# -----------------------------------------------------------------------------
# AUTH VIEW
# -----------------------------------------------------------------------------
if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 1.4, 1])
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.form("cinematic_auth_form"):
            st.markdown("""
                <div style="text-align: center; margin-bottom: 25px;">
                    <h1 style="font-family: 'Orbitron', sans-serif; font-size: 32px; font-weight: 800; background: linear-gradient(135deg, #60a5fa 0%, #c084fc 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0;">MINDGRAPH AI</h1>
                    <p style="color: #94a3b8; font-size: 10px; letter-spacing: 2px; font-weight: 600; margin-top: 6px;">ENTERPRISE KNOWLEDGE PLATFORM</p>
                </div>
            """, unsafe_allow_html=True)
            
            email = st.text_input("Enterprise Identity", placeholder="developer@company.com")
            password = st.text_input("Access Token", type="password", placeholder="••••••••••••")
            
            submit = st.form_submit_button("⚡ INITIALIZE SECURE SESSION")
            
            if submit:
                if email and password:
                    with st.spinner("Authenticating Token..."):
                        time.sleep(0.8)
                        st.session_state.authenticated = True
                        st.rerun()
                else:
                    st.error("Please provide valid credentials.")

# -----------------------------------------------------------------------------
# DASHBOARD WORKSPACE (AFTER LOGIN)
# -----------------------------------------------------------------------------
else:
    st.sidebar.title("MINDGRAPH AI")
    st.title("Workspace Dashboard")
    st.success("Authenticated Successfully!")
    
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()