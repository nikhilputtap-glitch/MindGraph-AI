import os
import json
import io
from datetime import datetime
import pg8000.native
import streamlit as st
from google import genai
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from supabase import create_client, Client

# Page Configuration
st.set_page_config(page_title="MindGraph AI - Secure Workspace", page_icon="🧠", layout="wide")

# -----------------------------------------------------------------------------
# GLOBAL HIGH-PRIORITY CYBERPUNK GLASSMORPHISM CSS
# -----------------------------------------------------------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Plus+Jakarta+Sans:wght@300;400;600&display=swap');

    /* Radial Dark Gradient Background */
    html, body, .stApp {
        background: radial-gradient(circle at 50% 30%, #0f172a 0%, #030712 100%) !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: #f8fafc !important;
    }

    /* Hide Top Nav & Footers */
    header[data-testid="stHeader"], footer {
        visibility: hidden !important;
        display: none !important;
    }

    .main .block-container {
        padding-top: 2rem !important;
        max-width: 1100px !important;
    }

    /* Target Login Input Boxes / Forms */
    div[data-baseweb="input"], div[data-baseweb="input"] input {
        background-color: rgba(30, 41, 59, 0.85) !important;
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

    /* Streamlit Primary Buttons Custom Glowing Overlay */
    button[kind="primary"], div.stButton > button {
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
        transition: all 0.3s ease !important;
    }

    button[kind="primary"]:hover, div.stButton > button:hover {
        box-shadow: 0 8px 30px rgba(124, 58, 237, 0.8) !important;
        transform: translateY(-2px) !important;
    }

    /* Custom Glass Card Styling for Expander Containers */
    div[data-testid="stExpander"] {
        background: rgba(15, 23, 42, 0.75) !important;
        border: 1px solid rgba(59, 130, 246, 0.3) !important;
        border-radius: 14px !important;
        backdrop-filter: blur(12px) !important;
    }

    /* Tab Header Styling */
    div[data-baseweb="tab-list"] {
        background: rgba(15, 23, 42, 0.8);
        border-radius: 12px;
        padding: 5px;
        border: 1px solid rgba(148, 163, 184, 0.2);
    }

    button[data-baseweb="tab"] {
        color: #94a3b8 !important;
        font-weight: 600;
    }

    button[aria-selected="true"] {
        color: #60a5fa !important;
        background: rgba(30, 41, 59, 0.9) !important;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# Secrets Retrieval
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
db_url = st.secrets.get("DATABASE_URL") or os.getenv("DATABASE_URL")
supabase_url = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
supabase_anon_key = st.secrets.get("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_ANON_KEY")

if not api_key or not db_url or not supabase_url or not supabase_anon_key:
    st.error("Missing configuration secrets! Please verify Streamlit Secrets.")
    st.stop()

# Initialize Clients
client = genai.Client(api_key=api_key)
supabase: Client = create_client(supabase_url, supabase_anon_key)

# Session State for Authentication
if "user" not in st.session_state:
    st.session_state.user = None

# Embedder Setup
@st.cache_resource
def load_embedder():
    return SentenceTransformer('all-MiniLM-L6-v2')

embedder = load_embedder()

# Database Connection Fix (Using Supabase IPv4 Pooler Session Mode Port 5432)
def get_db_connection():
    try:
        conn = pg8000.native.Connection(
            user="postgres.oxwiqxlwzctvblmvmtko",  # Pooler Username
            password="248b1A0452ps",
            host="aws-0-ap-south-1.pooler.supabase.com", # IPv4 Supported Pooler Host
            port=5432,
            database="postgres",
            ssl_context=True
        )
        return conn
    except Exception as e:
        st.error(f"Database Connection Error: {e}")
        return None

def init_db():
    conn = get_db_connection()
    if conn:
        try:
            conn.run('''
                CREATE TABLE IF NOT EXISTS decisions (
                    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                    user_email TEXT,
                    transcript TEXT,
                    decision TEXT,
                    rationale TEXT,
                    risks TEXT,
                    vector TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            ''')
            conn.close()
        except Exception as e:
            st.error(f"Failed to initialize database: {e}")

init_db()

# PDF Generation
def generate_pdf_report(records, report_title="MindGraph AI - Decision Audit Log"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, textColor=colors.HexColor('#1E293B'))
    subtitle_style = ParagraphStyle('DocSubTitle', parent=styles['Normal'], fontName='Helvetica', fontSize=10, textColor=colors.HexColor('#64748B'))
    heading2_style = ParagraphStyle('Heading2', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=11, textColor=colors.HexColor('#0F172A'))
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontName='Helvetica', fontSize=9, textColor=colors.HexColor('#334155'))
    bold_label = ParagraphStyle('BoldLabel', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, textColor=colors.HexColor('#1E293B'))
    
    story = [
        Paragraph(f"🧠 {report_title}", title_style),
        Spacer(1, 4),
        Paragraph("Enterprise Knowledge Base Report & Audit Records", subtitle_style),
        Spacer(1, 10),
        HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2563EB'), spaceAfter=15)
    ]
    
    for rec in records:
        r_id = rec[0]
        u_email = rec[1]
        trans = rec[2]
        dec = rec[3]
        rat = rec[4]
        rsk = rec[5]
        created_at = rec[6]

        story.append(Paragraph(f"Record #{r_id} | Created by: {u_email} | Date: {created_at}", heading2_style))
        story.append(Spacer(1, 4))
        
        table_data = [
            [Paragraph("Decision:", bold_label), Paragraph(str(dec), body_style)],
            [Paragraph("Rationale:", bold_label), Paragraph(str(rat), body_style)],
            [Paragraph("Identified Risks:", bold_label), Paragraph(str(rsk), body_style)],
        ]
        
        t = Table(table_data, colWidths=[100, 440])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(t)
        story.append(Spacer(1, 10))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# AI Core Logic
def extract_decision_logic(transcript: str):
    prompt = f"""
    Analyze the following developer chat transcript and extract key architecture/design decisions.
    Return ONLY a valid JSON object with keys: "decision", "rationale", "risks".
    
    Transcript:
    {transcript}
    """
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    text = response.text.strip()
    if text.startswith("```json"):
        text = text[7:-3].strip()
    return json.loads(text)

def save_decision(user_email, transcript, decision, rationale, risks):
    if isinstance(risks, (list, dict)):
        risks = ", ".join(risks) if isinstance(risks, list) else str(risks)
    if isinstance(decision, (list, dict)):
        decision = ", ".join(decision) if isinstance(decision, list) else str(decision)
    if isinstance(rationale, (list, dict)):
        rationale = ", ".join(rationale) if isinstance(rationale, list) else str(rationale)

    vec_bytes = embedder.encode(str(decision)).tobytes()
    vec_str = vec_bytes.hex()

    conn = get_db_connection()
    if conn:
        conn.run(
            "INSERT INTO decisions (user_email, transcript, decision, rationale, risks, vector) VALUES (:u, :t, :d, :r, :rk, :v)",
            u=user_email, t=str(transcript), d=str(decision), r=str(rationale), rk=str(risks), v=vec_str
        )
        conn.close()

def get_all_records():
    conn = get_db_connection()
    if conn:
        records = conn.run("SELECT id, user_email, transcript, decision, rationale, risks, created_at FROM decisions ORDER BY id DESC")
        conn.close()
        return records
    return []

# AUTHENTICATION UI (Only Sign In)
if st.session_state.user is None:
    st.markdown("""
        <div style="text-align: center; margin-top: 40px; margin-bottom: 20px;">
            <h1 style="font-family: 'Orbitron', sans-serif; font-size: 36px; font-weight: 800; background: linear-gradient(135deg, #60a5fa 0%, #c084fc 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">🧠 MindGraph AI</h1>
            <p style="color: #94a3b8; font-size: 12px; letter-spacing: 2px;">AUTHENTICATION PORTAL</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.3, 1])
    with col2:
        st.markdown("""
            <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(59, 130, 246, 0.4); box-shadow: 0 0 40px rgba(37, 99, 235, 0.35); border-radius: 20px; padding: 25px 25px 10px 25px;">
                <p style="text-align: center; color: #60a5fa; font-weight: 700; font-size: 13px; font-family: 'Orbitron'; letter-spacing: 1px;">🔒 SIGN IN TO WORKSPACE</p>
            </div>
        """, unsafe_allow_html=True)
        
        login_email = st.text_input("Email", key="l_email")
        login_password = st.text_input("Password", type="password", key="l_pass")
        
        if st.button("Sign In", type="primary", use_container_width=True):
            try:
                res = supabase.auth.sign_in_with_password({"email": login_email, "password": login_password})
                st.session_state.user = res.user
                st.success("Login Successful!")
                st.rerun()
            except Exception as e:
                st.error(f"Login Failed: {e}")

# LOGGED-IN DASHBOARD UI
else:
    # Sidebar User Profile
    st.sidebar.markdown('<h2 style="font-family: Orbitron; font-size: 20px; color: #60a5fa;">👤 User Profile</h2>', unsafe_allow_html=True)
    st.sidebar.write("Logged in as:")
    st.sidebar.info(st.session_state.user.email)
    
    if st.sidebar.button("Logout", type="secondary"):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.rerun()

    st.markdown('<h1 style="font-family: Orbitron; font-size: 32px; background: linear-gradient(135deg, #60a5fa 0%, #c084fc 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">🧠 MindGraph AI Dashboard</h1>', unsafe_allow_html=True)
    st.caption("Enterprise Tacit Knowledge Portal (Authenticated)")

    tab1, tab2, tab3 = st.tabs(["📝 Extract Decision", "🔍 Vector RAG Search", "📊 Knowledge Base & Audit"])

    with tab1:
        st.subheader("Process Chat Transcript")
        transcript_input = st.text_area("Paste Developer Chat / Slack Logs Here:", height=200)
        
        if st.button("Extract & Index Decision", type="primary"):
            if transcript_input.strip():
                with st.spinner("Analyzing with Gemini..."):
                    try:
                        data = extract_decision_logic(transcript_input)
                        save_decision(
                            st.session_state.user.email,
                            transcript_input,
                            data.get("decision", ""),
                            data.get("rationale", ""),
                            data.get("risks", "")
                        )
                        st.success("Decision indexed under your account!")
                        st.json(data)
                    except Exception as e:
                        st.error(f"Extraction Error: {e}")
            else:
                st.warning("Please enter a transcript first.")

    with tab2:
        st.subheader("Semantic Vector RAG Search")
        query = st.text_input("Search historical decisions:")
        
        if query:
            conn = get_db_connection()
            if conn:
                rows = conn.run("SELECT id, decision, rationale, risks, vector FROM decisions")
                conn.close()
                
                if rows:
                    query_vec = embedder.encode(query)
                    results = []
                    for r_id, dec, rat, rsk, vec_hex in rows:
                        if vec_hex:
                            try:
                                doc_bytes = bytes.fromhex(vec_hex)
                                doc_vec = np.frombuffer(doc_bytes, dtype=np.float32)
                                sim = cosine_similarity([query_vec], [doc_vec])[0][0]
                                results.append((sim, dec, rat, rsk))
                            except Exception:
                                pass
                    
                    results.sort(key=lambda x: x[0], reverse=True)
                    for sim, dec, rat, rsk in results[:5]:
                        with st.expander(f"🎯 Match Confidence: {sim*100:.1f}% - {str(dec)[:60]}..."):
                            st.write(f"**Decision:** {dec}")
                            st.write(f"**Rationale:** {rat}")
                            st.write(f"**Identified Risks:** {rsk}")
                else:
                    st.info("No decisions found.")

    with tab3:
        st.subheader("Indexed Organizational Memory & Audit Reports")
        records = get_all_records()
        
        if records:
            pdf_data = generate_pdf_report(records)
            st.download_button(
                label="📥 Download Complete Audit Report (PDF)",
                data=pdf_data,
                file_name="MindGraph_Audit_Log.pdf",
                mime="application/pdf",
                type="primary"
            )
            st.divider()
            for rec in records:
                r_id = rec[0]
                u_email = rec[1]
                trans = rec[2]
                dec = rec[3]
                rat = rec[4]
                rsk = rec[5]
                created_at = rec[6]
                with st.expander(f"Record #{r_id} | Author: {u_email} | {str(dec)[:60]}"):
                    st.write(f"**Author:** {u_email}")
                    st.write(f"**Decision:** {dec}")
                    st.write(f"**Rationale:** {rat}")
                    st.write(f"**Risks:** {rsk}")
                    st.text_area("Original Log", trans, height=100, disabled=True, key=f"raw_{r_id}")
        else:
            st.info("Knowledge base is empty.")