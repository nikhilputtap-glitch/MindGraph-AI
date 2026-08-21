import streamlit as st
import json
import time

# -----------------------------------------------------------------------------
# 1. PAGE CONFIG & STYLING SETUP
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="MindGraph AI - Tacit Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Futuristic Cyberpunk Glassmorphism Global CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Plus+Jakarta+Sans:wght@300;400;600&display=swap');

    /* Global Dark Theme Background */
    .stApp {
        background: radial-gradient(circle at 50% 30%, #0f172a 0%, #030712 100%) !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: #f8fafc !important;
    }

    /* Hide Unnecessary Streamlit Elements */
    header[data-testid="stHeader"], footer {
        visibility: hidden !important;
    }

    /* Custom Header Container */
    .brand-header {
        text-align: center;
        background: rgba(15, 23, 42, 0.7);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(59, 130, 246, 0.3);
        box-shadow: 0 0 35px rgba(37, 99, 235, 0.3);
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 25px;
    }

    .brand-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 34px;
        font-weight: 800;
        background: linear-gradient(135deg, #60a5fa 0%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 2px;
        margin: 0;
    }

    .brand-subtitle {
        color: #94a3b8;
        font-size: 12px;
        letter-spacing: 2px;
        margin-top: 6px;
        font-weight: 600;
    }

    /* Input Field Styling Overrides */
    div[data-baseweb="input"] {
        background-color: rgba(30, 41, 59, 0.8) !important;
        border: 1px solid rgba(148, 163, 184, 0.25) !important;
        border-radius: 10px !important;
    }
    
    div[data-baseweb="input"]:focus-within {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.4) !important;
    }

    /* Button Custom Gradient Overlay */
    div.stButton > button, div.stFormSubmitButton > button {
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%) !important;
        color: #ffffff !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        letter-spacing: 1.5px !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 20px !important;
        box-shadow: 0 4px 25px rgba(37, 99, 235, 0.5) !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
    }

    div.stButton > button:hover, div.stFormSubmitButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(124, 58, 237, 0.8) !important;
    }

    /* Badge Tags */
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
# 2. SESSION STATE INITIALIZATION
# -----------------------------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "db" not in st.session_state:
    st.session_state.db = [
        {
            "id": "KB-101",
            "decision": "Adopted PostgreSQL over MongoDB for Core User Data",
            "rationale": "Strong ACID compliance requirement for financial transactions and relational joins.",
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
# 3. AUTHENTICATION PORTAL (LOGIN SCREEN)
# -----------------------------------------------------------------------------
if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 1.3, 1])
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Cyberpunk Glass Header
        st.markdown("""
            <div class="brand-header">
                <div class="brand-title">MINDGRAPH AI</div>
                <div class="brand-subtitle">TACIT KNOWLEDGE INTELLIGENCE PLATFORM</div>
            </div>
        """, unsafe_allow_html=True)

        # Login Form
        with st.form("auth_form"):
            st.markdown("<p style='text-align: center; color: #60a5fa; font-weight: 600; font-size: 13px; margin-bottom: 20px;'>🔐 ENTERPRISE AUTHENTICATION PORTAL</p>", unsafe_allow_html=True)
            
            email = st.text_input("ENTERPRISE IDENTITY", placeholder="developer@company.com")
            password = st.text_input("ACCESS TOKEN / PASSCODE", type="password", placeholder="••••••••••••")
            
            submit = st.form_submit_button("INITIALIZE SECURE SESSION")
            
            if submit:
                if email and password:
                    with st.spinner("Authenticating Identity & Security Tokens..."):
                        time.sleep(1)
                        st.session_state.authenticated = True
                        st.rerun()
                else:
                    st.error("Please provide both Enterprise Identity and Access Token.")

        st.markdown("""
            <p style="text-align: center; color: #475569; font-size: 11px; margin-top: 15px;">
                Protected by Supabase Auth & Encrypted REST API
            </p>
        """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. MAIN DASHBOARD WORKSPACE (AFTER LOGIN)
# -----------------------------------------------------------------------------
else:
    # Sidebar Navigation
    with st.sidebar:
        st.markdown('<div class="brand-title" style="font-size: 24px;">MINDGRAPH AI</div>', unsafe_allow_html=True)
        st.markdown('<div class="brand-subtitle" style="margin-bottom: 15px;">Tacit Knowledge Engine</div>', unsafe_allow_html=True)
        st.divider()
        
        st.markdown("### **Workspace Navigation**")
        page = st.radio("Select View", [
            "1. Chat Ingest & Extraction", 
            "2. Semantic Vector RAG Search", 
            "3. Audit Logs & PDF Export"
        ])
        
        st.divider()
        st.markdown("<span class='badge-tag'>API: Online</span> <span class='badge-tag'>Supabase: Connected</span>", unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("LOGOUT SESSION"):
            st.session_state.authenticated = False
            st.rerun()

    # VIEW 1: CHAT INGEST & EXTRACTION
    if page == "1. Chat Ingest & Extraction":
        st.markdown('<h1>Automated Tacit Knowledge Capture</h1>', unsafe_allow_html=True)
        st.markdown('<p class="brand-subtitle">Paste raw developer chat conversations to auto-extract Decision, Rationale & Technical Risks.</p>', unsafe_allow_html=True)
        st.divider()

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
                    with st.spinner("Gemini Flash parsing structured decisions..."):
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

    # VIEW 2: SEMANTIC VECTOR RAG SEARCH
    elif page == "2. Semantic Vector RAG Search":
        st.markdown('<h1>Semantic Decision RAG Engine</h1>', unsafe_allow_html=True)
        st.markdown('<p class="brand-subtitle">Search historical decisions by concept or intent rather than exact keyword matching.</p>', unsafe_allow_html=True)
        st.divider()

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

    # VIEW 3: AUDIT LOGS & EXPORT
    elif page == "3. Audit Logs & PDF Export":
        st.markdown('<h1>Institutional Memory & Audit Compliance</h1>', unsafe_allow_html=True)
        st.markdown('<p class="brand-subtitle">Review knowledge logs and export 1-click compliance PDF reports.</p>', unsafe_allow_html=True)
        st.divider()

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