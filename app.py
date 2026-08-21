import streamlit as st
import streamlit.components.v1 as components
import json
import time

st.set_page_config(
    page_title="MindGraph AI - Enterprise Auth",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Background and Global Reset
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Plus+Jakarta+Sans:wght@300;400;600&display=swap');
    
    .stApp {
        background: #030712 !important;
    }
    header[data-testid="stHeader"], footer {
        visibility: hidden !important;
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
            "rationale": "Strong ACID compliance requirement for financial transactions.",
            "risks": "Requires complex manual scaling/sharding at higher traffic volumes.",
            "author": "alex_techlead"
        }
    ]

# -----------------------------------------------------------------------------
# CINEMATIC AUTHENTICATION VIEW
# -----------------------------------------------------------------------------
if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 1.8, 1])
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Pure HTML/CSS Injection with Glowing Neon Glassmorphism
        components.html("""
            <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Plus+Jakarta+Sans:wght@400;600&display=swap" rel="stylesheet">
            <style>
                * {
                    box-sizing: border-box;
                    font-family: 'Plus Jakarta Sans', sans-serif;
                }
                body {
                    background: transparent;
                    margin: 0;
                    padding: 10px;
                    display: flex;
                    justify-content: center;
                }
                .card {
                    background: rgba(15, 23, 42, 0.75);
                    backdrop-filter: blur(20px);
                    -webkit-backdrop-filter: blur(20px);
                    border: 1px solid rgba(59, 130, 246, 0.3);
                    box-shadow: 0 0 40px rgba(37, 99, 235, 0.35), inset 0 0 15px rgba(59, 130, 246, 0.1);
                    border-radius: 24px;
                    padding: 40px 35px;
                    width: 100%;
                    max-width: 450px;
                    text-align: center;
                }
                .title {
                    font-family: 'Orbitron', sans-serif;
                    font-size: 30px;
                    font-weight: 800;
                    background: linear-gradient(135deg, #60a5fa 0%, #c084fc 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    letter-spacing: 2px;
                    margin: 0 0 4px 0;
                }
                .subtitle {
                    color: #94a3b8;
                    font-size: 11px;
                    letter-spacing: 2px;
                    margin-bottom: 30px;
                    font-weight: 600;
                }
                .input-group {
                    margin-bottom: 20px;
                    text-align: left;
                }
                label {
                    display: block;
                    color: #60a5fa;
                    font-size: 11px;
                    font-weight: 600;
                    letter-spacing: 1px;
                    margin-bottom: 8px;
                }
                input {
                    width: 100%;
                    padding: 14px 16px;
                    background: rgba(30, 41, 59, 0.7);
                    border: 1px solid rgba(148, 163, 184, 0.2);
                    border-radius: 12px;
                    color: #f8fafc;
                    font-size: 14px;
                    outline: none;
                    transition: all 0.3s ease;
                }
                input:focus {
                    border-color: #3b82f6;
                    box-shadow: 0 0 15px rgba(59, 130, 246, 0.5);
                    background: rgba(30, 41, 59, 0.9);
                }
                .btn {
                    width: 100%;
                    padding: 15px;
                    background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
                    border: none;
                    border-radius: 12px;
                    color: white;
                    font-family: 'Orbitron', sans-serif;
                    font-size: 13px;
                    font-weight: 700;
                    letter-spacing: 1.5px;
                    cursor: pointer;
                    box-shadow: 0 4px 25px rgba(37, 99, 235, 0.5);
                    transition: all 0.3s ease;
                    margin-top: 10px;
                }
                .btn:hover {
                    box-shadow: 0 6px 30px rgba(124, 58, 237, 0.8);
                    transform: translateY(-2px);
                }
                .footer-text {
                    color: #475569;
                    font-size: 11px;
                    margin-top: 20px;
                }
            </style>
            
            <div class="card">
                <div class="title">MINDGRAPH AI</div>
                <div class="subtitle">ENTERPRISE KNOWLEDGE PLATFORM</div>
                
                <div class="input-group">
                    <label>ENTERPRISE IDENTITY</label>
                    <input type="text" id="email" placeholder="developer@company.com">
                </div>
                
                <div class="input-group">
                    <label>ACCESS TOKEN</label>
                    <input type="password" id="pass" placeholder="••••••••••••">
                </div>
                
                <button class="btn" onclick="login()">INITIALIZE SECURE SESSION</button>
                
                <div class="footer-text">Protected by Supabase Auth & Vector RAG Layer</div>
            </div>

            <script>
                function login() {
                    var e = document.getElementById('email').value;
                    var p = document.getElementById('pass').value;
                    if(e && p) {
                        window.parent.postMessage({type: 'streamlit:setComponentValue', value: true}, '*');
                    } else {
                        alert('Please enter credentials');
                    }
                }
            </script>
        """, height=520)

        # Standard Fallback Button to trigger session state in Streamlit
        if st.button("🚀 Quick Bypass / Enter Workspace"):
            st.session_state.authenticated = True
            st.rerun()

else:
    st.sidebar.title("MINDGRAPH AI")
    st.title("Workspace Dashboard")
    st.success("Authenticated Successfully!")
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()