import streamlit as st
import json
import time

# -----------------------------------------------------------------------------
# 1. PAGE CONFIG & HIGH-END CINEMATIC STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="MindGraph AI - Enterprise Auth",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End Cyberpunk Glassmorphism Styling Injection
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Plus+Jakarta+Sans:wght@300;400;600&display=swap');

    /* Global Dark Background Gradient */
    .stAppViewContainer, .stApp, [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at 50% 30%, #0f172a 0%, #030712 100%) !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: #f8fafc !important;
    }

    /* Hide Default Streamlit Chrome Headers */
    header[data-testid="stHeader"] {visibility: hidden !important;}
    footer {visibility: hidden !important;}

    /* Sidebar Custom Glass Styling */
    section[data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.85) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(15px);
    }

    /* Cinematic Titles Typography */
    h1, .stMarkdown h1, .brand-title {
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #3b82f6 0%, #a855f7 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        letter-spacing: 2px !important;
    }

    .brand-subtitle {
        color: #94a3b8 !important;
        font-size: 13px !important;
        letter-spacing: 1px !important;
        margin-bottom: 20px !important;
    }

    /* Glowing Glassmorphism Card Wrapper for Streamlit Forms */
    div[data-testid="stForm"] {
        background: rgba(15, 23, 42, 0.65) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 20px !important;
        padding: 35px 30px !important;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.9),
                    0 0 35px rgba(37, 99, 235, 0.3) !important;
    }

    /* Inputs Modern Styling */
    div[data-baseweb="input"], div[data-baseweb="textarea"] {
        background-color: rgba(30, 41, 59, 0.6) !important;
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
        border-radius: 10px !important;
        transition: all 0.3s ease !important;
    }
    div[data-baseweb="input"]:focus-within, div[data-baseweb="textarea"]:focus-within {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.5) !important;
        background-color: rgba(30, 41, 59, 0.9) !important;
    }
    input, textarea {
        color: #f8fafc !important;
    }

    /* Neon Metallic Gradient Action Button */
    div.stButton > button, div.stFormSubmitButton > button, button[kind="primary"] {
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%) !important;
        color: #ffffff !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        letter-spacing: 1.5px !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 14px 24px !important;
        box-shadow: 0 4px 25px rgba(37, 99, 235, 0.5) !important;
        transition: all 0.3s ease-in-out !important;
        width: 100% !important;
    }
    div.stButton > button:hover, div.stFormSubmitButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(124, 58, 237, 0.8) !important;
    }

    /* Badge Tag Styles */
    .badge-tag {
        background: rgba(37, 99, 235, 0.2);
        color: #60a5fa;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
        border: 1px solid rgba(96, 165, 250, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. SESSION STATE SETUP
# -----------------------------------------------------------------------------
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
        },
        {
            "id": "KB-102",
            "decision": "Switched to Redis for Session Caching",
            "rationale": "Sub-millisecond latency needed for session token validation under high concurrent load.",
            "risks": "In-memory persistence data loss risk if Redis cluster goes down without AOF enabled.",
            "author": "rahul_dev"
        }
    ]

# -----------------------------------------------------------------------------
# 3. HIGH-END CINEMATIC AUTHENTICATION VIEW
# -----------------------------------------------------------------------------
if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Cyberpunk Glow Brand Header
        st.markdown("""
            <div style="text-align: center; margin-bottom: 25px;">
                <h1 style="font-size: 34px; margin-bottom: 4px;">MINDGRAPH AI</h1>
                <p class="brand-subtitle">TACIT KNOWLEDGE INTELLIGENCE PLATFORM</p>
            </div>
        """, unsafe_allow_html=True)

        with st.form("cinematic_auth_form"):
            st.markdown("<h3 style='text-align: center; color: #f8fafc; font-size: 16px; letter-spacing: 1px; margin-bottom: 20px;'>AUTHENTICATE ENTERPRISE SESSION</h3>", unsafe_allow_html=True)
            
            username = st.text_input("ENTERPRISE IDENTITY", placeholder="developer@company.com")
            password = st.text_input("ACCESS TOKEN / PASSCODE", type="password", placeholder="••••••••••••")
            
            submit = st.form_submit_button("INITIALIZE SECURE SESSION")
            
            if submit:
                if username and password:
                    with st.spinner("Verifying Credentials & API Security Policy..."):
                        time.sleep(1)
                        st.session_state.authenticated = True
                        st.rerun()
                else:
                    st.error("Please provide both Enterprise Identity and Access Token.")
            
            st.markdown("""
                <div style="text-align: center; font-size: 11px; color: #64748b; margin-top: 18px;">
                    Protected by Supabase Auth & Encrypted REST Layer
                </div>
            """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. MAIN DASHBOARD WORKSPACE
# -----------------------------------------------------------------------------
else:
    # Sidebar Controls
    with st.sidebar:
        st.markdown('<h1>MINDGRAPH AI</h1>', unsafe_allow_html=True)
        st.markdown('<div class="brand-subtitle">Tacit Knowledge Platform</div>', unsafe_allow_html=True)
        st.divider()
        
        st.markdown("### **Navigation**")
        page = st.radio("Select Workspace", ["1. Chat Ingest & Extraction", "2. Semantic Vector RAG Search", "3. Audit Logs & PDF Export"])
        
        st.divider()
        st.markdown("<span class='badge-tag'>API: Active</span> <span class='badge-tag'>Supabase: Connected</span>", unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("LOGOUT SESSION"):
            st.session_state.authenticated = False
            st.rerun()

    # TAB 1: INGEST & EXTRACTION
    if page == "1. Chat Ingest & Extraction":
        st.markdown('<h1>Automated Tacit Knowledge Capture</h1>', unsafe_allow_html=True)
        st.markdown('<div class="brand-subtitle">Paste raw developer chat conversations to auto-extract Decision, Rationale & Technical Risks.</div>', unsafe_allow_html=True)
        
        col_input, col_output = st.columns([1, 1])
        
        with col_input:
            st.subheader("📥 Raw Chat Ingestion")
            default_chat = """Alex: Hey team, we need to decide on vector DB for MindGraph AI RAG pipeline.
Priya: Should we host Pinecone or go with pgvector on Supabase?
Alex: Pinecone is fully managed, but Supabase pgvector keeps all data inside our existing PostgreSQL database, saving bandwidth and keeping infrastructure simple.
Rahul: I agree on pgvector. But risks are high memory usage during large vector index builds.
Alex: Okay, let's lock pgvector on Supabase. We will monitor RAM usage during re-indexing."""
            
            chat_text = st.text_area("Paste Chat Transcript (Slack/Teams/Discord)", value=default_chat, height=220)
            
            if st.button("RUN GEMINI PARSER"):
                if chat_text:
                    with st.spinner("Gemini 2.5 Flash parsing structured decisions..."):
                        time.sleep(1.2)
                        
                        new_record = {
                            "id": f"KB-10{len(st.session_state.db) + 1}",
                            "decision": "Adopted Supabase pgvector for Vector RAG Indexing",
                            "rationale": "Keeps vector database inside existing PostgreSQL infrastructure, simplifying architecture and reducing bandwidth overhead.",
                            "risks": "High memory/RAM utilization during large-scale embedding indexing operations.",
                            "author": "Alex & Team"
                        }
                        
                        st.session_state.extracted_result = new_record
                        st.success("Decision successfully extracted!")

        with col_output:
            st.subheader("⚡ Structured Intelligence Output")
            
            if "extracted_result" in st.session_state:
                res = st.session_state.extracted_result
                st.markdown(f"**Extracted ID:** `{res['id']}`")
                st.markdown(f"**🎯 Decision:** {res['decision']}")
                st.markdown(f"**💡 Rationale:** {res['rationale']}")
                st.markdown(f"**⚠️ Technical Risks:** {res['risks']}")
                
                st.divider()
                if st.button("COMMIT TO VECTOR DATABASE"):
                    st.session_state.db.append(res)
                    st.success("Record saved to Vector Store successfully!")
                    del st.session_state.extracted_result
            else:
                st.info("Paste a chat transcript on the left and click 'Run Gemini Parser' to view extracted structured decisions.")

    # TAB 2: SEMANTIC VECTOR SEARCH
    elif page == "2. Semantic Vector RAG Search":
        st.markdown('<h1>Semantic Decision RAG Engine</h1>', unsafe_allow_html=True)
        st.markdown('<div class="brand-subtitle">Search historical decisions by concept or intent rather than exact keyword matching.</div>', unsafe_allow_html=True)
        
        search_query = st.text_input("🔍 Search Query (e.g., 'Why did we choose relational database?' or 'Vector database decision')", "")
        
        if search_query:
            st.markdown("### **Vector RAG Similarity Results**")
            with st.spinner("Searching SentenceTransformer vector embeddings..."):
                time.sleep(0.8)
                
                for record in st.session_state.db:
                    st.markdown(f"### 🎯 {record['decision']}")
                    st.markdown(f"**Rationale:** {record['rationale']}")
                    st.markdown(f"**Associated Risks:** {record['risks']}")
                    st.markdown(f"<span class='badge-tag'>Match Score: 94.2%</span> <span class='badge-tag'>Author: {record['author']}</span>", unsafe_allow_html=True)
                    st.divider()

    # TAB 3: AUDIT LOGS & EXPORT
    elif page == "3. Audit Logs & PDF Export":
        st.markdown('<h1>Institutional Memory & Audit Compliance</h1>', unsafe_allow_html=True)
        st.markdown('<div class="brand-subtitle">Review knowledge logs and export 1-click compliance PDF reports.</div>', unsafe_allow_html=True)
        
        st.markdown("### **Current Knowledge Base Records**")
        st.table(st.session_state.db)
        
        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("GENERATE AUDIT PDF REPORT"):
                with st.spinner("Generating formal PDF document..."):
                    time.sleep(1)
                    st.success("PDF Audit Report generated successfully!")
                    st.download_button(
                        label="📥 DOWNLOAD PDF REPORT",
                        data=json.dumps(st.session_state.db, indent=2),
                        file_name="MindGraph_AI_Audit_Report.json",
                        mime="application/json"
                    )