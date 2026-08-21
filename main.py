import os
import json
import io
from datetime import datetime
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

# Secrets Retrieval
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
supabase_url = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
supabase_anon_key = st.secrets.get("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_ANON_KEY")

if not api_key or not supabase_url or not supabase_anon_key:
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
        r_id = rec.get("id")
        u_email = rec.get("user_email")
        trans = rec.get("transcript")
        dec = rec.get("decision")
        rat = rec.get("rationale")
        rsk = rec.get("risks")
        created_at = rec.get("created_at")

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

# Save via REST API (No DB connection / Tenant Error)
def save_decision(user_email, transcript, decision, rationale, risks):
    if isinstance(risks, (list, dict)):
        risks = ", ".join(risks) if isinstance(risks, list) else str(risks)
    if isinstance(decision, (list, dict)):
        decision = ", ".join(decision) if isinstance(decision, list) else str(decision)
    if isinstance(rationale, (list, dict)):
        rationale = ", ".join(rationale) if isinstance(rationale, list) else str(rationale)

    vec_list = embedder.encode(str(decision)).tolist()
    
    data = {
        "user_email": user_email,
        "transcript": str(transcript),
        "decision": str(decision),
        "rationale": str(rationale),
        "risks": str(risks),
        "vector": str(vec_list) # Json formatted vector list for storage
    }
    
    try:
        supabase.table("decisions").insert(data).execute()
    except Exception as e:
        st.error(f"Error saving to database: {e}")

# Fetch via REST API
def get_all_records():
    try:
        res = supabase.table("decisions").select("*").order("id", desc=True).execute()
        return res.data
    except Exception as e:
        st.error(f"Error fetching records: {e}")
        return []

# AUTHENTICATION UI (Only Sign In)
if st.session_state.user is None:
    st.title("🧠 MindGraph AI - Authentication Portal")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("🔒 Sign In to your Workspace")
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
    st.sidebar.title("👤 User Profile")
    st.sidebar.write("Logged in as:")
    st.sidebar.info(st.session_state.user.email)
    
    if st.sidebar.button("Logout", type="secondary"):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.rerun()

    st.title("🧠 MindGraph AI Dashboard")
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
            rows = get_all_records()
            if rows:
                query_vec = embedder.encode(query)
                results = []
                for r in rows:
                    vec_raw = r.get("vector")
                    dec = r.get("decision")
                    rat = r.get("rationale")
                    rsk = r.get("risks")
                    
                    if vec_raw:
                        try:
                            doc_vec = np.array(json.loads(vec_raw), dtype=np.float32)
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
                r_id = rec.get("id")
                u_email = rec.get("user_email")
                trans = rec.get("transcript")
                dec = rec.get("decision")
                rat = rec.get("rationale")
                rsk = rec.get("risks")
                
                with st.expander(f"Record #{r_id} | Author: {u_email} | {str(dec)[:60]}"):
                    st.write(f"**Author:** {u_email}")
                    st.write(f"**Decision:** {dec}")
                    st.write(f"**Rationale:** {rat}")
                    st.write(f"**Risks:** {rsk}")
                    st.text_area("Original Log", trans, height=100, disabled=True, key=f"raw_{r_id}")
        else:
            st.info("Knowledge base is empty.")