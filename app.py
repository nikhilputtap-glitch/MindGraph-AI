import streamlit as st
import json
import time

st.set_page_config(
    page_title="MindGraph AI - Enterprise Auth",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# FORCE ULTRA CINEMATIC GLASSMORPHISM STYLING
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Plus+Jakarta+Sans:wght@300;400;600&display=swap');

    /* Global Background */
    .stApp {
        background: radial-gradient(circle at 50% 30%, #0f172a 0%, #030712 100%) !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* Hide Headers */
    header[data-testid="stHeader"], footer {
        visibility: hidden !important;
    }

    /* Modern Card Layout */
    .auth-card {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(59, 130, 246, 0.3);
        box-shadow: 0 0 35px rgba(37, 99, 235, 0.35);
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        margin-bottom: 20px;
    }

    .auth-title {
        font-family: 'Orbitron', sans-serif !important;
        font-size: 32px !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #3b82f6 0%, #a855f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }

    /* Button Override */
    div.stButton > button, div.stFormSubmitButton > button {
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%) !important;
        color: #ffffff !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 20px !important;
        box-shadow: 0 4px 20px rgba(37, 99, 235, 0.5) !important;
        width: 100% !important;
    }

    div.stButton > button:hover, div.stFormSubmitButton > button:hover {
        box-shadow: 0 6px 25px rgba(124, 58, 237, 0.8) !important;
        transform: translateY(-2px);
    }
    </style>
""", unsafe_allow_html=True)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "db" not in st.session_state:
    st.session_state.db = [
        {
            "id": "KB-101",
            "decision": "Adopted PostgreSQL over MongoDB for Core User Data",
            "rationale": "Strong ACID compliance requirement for financial transactions and structured relational joins.",
            "risks": "Requires complex manual scaling/sharding at higher traffic volumes.",
            "author": "alex_techlead"
        }
    ]

# AUTHENTICATION SCREEN
if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 1.3, 1])
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Pure HTML Custom Glass Card Header
        st.markdown("""
            <div class="auth-card">
                <div class="auth-title">MINDGRAPH AI</div>
                <p style="color: #94a3b8; font-size: 11px; letter-spacing: 2px; margin: 0;">TACIT KNOWLEDGE INTELLIGENCE PLATFORM</p>
            </div>
        """, unsafe_allow_html=True)

        with st.form("cinematic_auth_form"):
            st.markdown("<p style='text-align: center; color: #60a5fa; font-weight: 600; font-size: 13px; margin-bottom: 15px;'>🔐 ENTERPRISE AUTHENTICATION</p>", unsafe_allow_html=True)
            
            username = st.text_input("ENTERPRISE IDENTITY", placeholder="developer@company.com")
            password = st.text_input("ACCESS TOKEN", type="password", placeholder="••••••••••••")
            
            submit = st.form_submit_button("INITIALIZE SECURE SESSION")
            
            if submit:
                if username and password:
                    with st.spinner("Authenticating Identity..."):
                        time.sleep(0.8)
                        st.session_state.authenticated = True
                        st.rerun()
                else:
                    st.error("Please enter credentials.")

else:
    st.sidebar.title("MINDGRAPH AI")
    st.title("Workspace Dashboard")
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()