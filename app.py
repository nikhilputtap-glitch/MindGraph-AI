import os
import sqlite3
import json
import io
from datetime import datetime
import streamlit as st
from google import genai
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Page Configuration
st.set_page_config(page_title="MindGraph AI", page_icon="🧠", layout="wide")

# API Key & Gemini Setup
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("GEMINI_API_KEY Missing! Add it to Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=api_key)

# Load Embedding Model
@st.cache_resource
def load_embedder():
    return SentenceTransformer('all-MiniLM-L6-v2')

embedder = load_embedder()

# Database Setup
DB_FILE = "mindgraph.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transcript TEXT,
            decision TEXT,
            rationale TEXT,
            risks TEXT,
            vector BLOB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# PDF Generation Function
def generate_pdf_report(records, report_title="MindGraph AI - Decision Architecture Audit Log"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1E293B')
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#64748B')
    )
    heading2_style = ParagraphStyle(
        'Heading2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#0F172A')
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155')
    )
    bold_label = ParagraphStyle(
        'BoldLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#1E293B')
    )
    
    story = []
    
    story.append(Paragraph(f"🧠 {report_title}", title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Enterprise Tacit Knowledge Base Report & Audit Records", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2563EB'), spaceAfter=15))
    
    for rec in records:
        r_id, trans, dec, rat, rsk, created_at = rec
        date_str = created_at if created_at else "N/A"
        story.append(Paragraph(f"Record #{r_id} | Date: {date_str}", heading2_style))
        story.append(Spacer(1, 6))
        
        table_data = [
            [Paragraph("Decision:", bold_label), Paragraph(dec, body_style)],
            [Paragraph("Rationale:", bold_label), Paragraph(rat, body_style)],
            [Paragraph("Identified Risks:", bold_label), Paragraph(rsk, body_style)],
        ]
        
        t = Table(table_data, colWidths=[100, 440])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#334155')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(t)
        story.append(Spacer(1, 12))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# Core Logic: Gemini Extraction
def extract_decision_logic(transcript: str):
    prompt = f"""
    Analyze the following developer chat transcript and extract key architecture/design decisions.
    Return ONLY a valid JSON object with keys: "decision", "rationale", "risks".
    
    Transcript:
    {transcript}
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    
    text = response.text.strip()
    if text.startswith("```json"):
        text = text[7:-3].strip()
    return json.loads(text)

# Database Operations
def save_decision(transcript, decision, rationale, risks):
    vec = embedder.encode(decision).tobytes()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO decisions (transcript, decision, rationale, risks, vector) VALUES (?, ?, ?, ?, ?)",
        (transcript, decision, rationale, risks, vec)
    )
    conn.commit()
    conn.close()

def get_all_records():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, transcript, decision, rationale, risks, created_at FROM decisions ORDER BY id DESC")
    records = cursor.fetchall()
    conn.close()
    return records

# UI Header
st.title("🧠 MindGraph AI")
st.caption("Enterprise Tacit Knowledge Extractor & RAG Engine")

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
                        transcript_input,
                        data.get("decision", ""),
                        data.get("rationale", ""),
                        data.get("risks", "")
                    )
                    st.success("Decision extracted and vector indexed successfully!")
                    st.json(data)
                except Exception as e:
                    st.error(f"Extraction Error: {e}")
        else:
            st.warning("Please enter a transcript first.")

with tab2:
    st.subheader("Semantic Vector RAG Search")
    query = st.text_input("Search historical decisions using natural language:")
    
    if query:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, decision, rationale, risks, vector FROM decisions")
        rows = cursor.fetchall()
        conn.close()
        
        if rows:
            query_vec = embedder.encode(query)
            results = []
            
            for r_id, dec, rat, rsk, blob in rows:
                if blob:
                    import numpy as np
                    doc_vec = np.frombuffer(blob, dtype=np.float32)
                    sim = cosine_similarity([query_vec], [doc_vec])[0][0]
                    results.append((sim, dec, rat, rsk))
            
            results.sort(key=lambda x: x[0], reverse=True)
            
            for sim, dec, rat, rsk in results[:5]:
                with st.expander(f"🎯 Match Confidence: {sim*100:.1f}% - {dec[:60]}..."):
                    st.write(f"**Decision:** {dec}")
                    st.write(f"**Rationale:** {rat}")
                    st.write(f"**Identified Risks:** {rsk}")
        else:
            st.info("No indexed decisions found in database.")

with tab3:
    st.subheader("Indexed Organizational Memory & Custom Audit Reports")
    records = get_all_records()
    
    if records:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            filter_mode = st.radio("Filter By:", ["All Time", "By Month", "By Year", "By Specific Date"])
        
        display_records = []
        report_title = "MindGraph AI - Decision Audit Report"
        file_suffix = "Full_Report"
        
        with col2:
            if filter_mode == "All Time":
                display_records = records
                report_title = "MindGraph AI - All Time Decision Audit Report"
                file_suffix = "All_Time"
                
            elif filter_mode == "By Month":
                months_dict = {}
                for r in records:
                    created_at = r[5]
                    if created_at:
                        try:
                            dt = datetime.strptime(created_at.split()[0], "%Y-%m-%d")
                            m_key = dt.strftime("%B %Y")
                        except Exception:
                            m_key = "Other"
                        months_dict.setdefault(m_key, []).append(r)
                
                sel_m = st.selectbox("Select Month:", options=list(months_dict.keys()))
                display_records = months_dict.get(sel_m, [])
                report_title = f"MindGraph AI - {sel_m} Monthly Audit Report"
                file_suffix = sel_m.replace(" ", "_") if sel_m else "Month"
                
            elif filter_mode == "By Year":
                years_dict = {}
                for r in records:
                    created_at = r[5]
                    if created_at:
                        try:
                            dt = datetime.strptime(created_at.split()[0], "%Y-%m-%d")
                            y_key = dt.strftime("%Y")
                        except Exception:
                            y_key = "Other"
                        years_dict.setdefault(y_key, []).append(r)
                
                sel_y = st.selectbox("Select Year:", options=list(years_dict.keys()))
                display_records = years_dict.get(sel_y, [])
                report_title = f"MindGraph AI - {sel_y} Annual Audit Report"
                file_suffix = f"Year_{sel_y}" if sel_y else "Year"
                
            elif filter_mode == "By Specific Date":
                sel_date = st.date_input("Select Date:", value=datetime.now())
                target_date_str = sel_date.strftime("%Y-%m-%d")
                
                for r in records:
                    created_at = r[5]
                    if created_at and created_at.startswith(target_date_str):
                        display_records.append(r)
                        
                report_title = f"MindGraph AI - {target_date_str} Daily Audit Report"
                file_suffix = f"Date_{target_date_str}"

        st.divider()
        
        if display_records:
            pdf_data = generate_pdf_report(display_records, report_title=report_title)
            st.download_button(
                label=f"📥 Download {report_title} (PDF)",
                data=pdf_data,
                file_name=f"MindGraph_Audit_{file_suffix}.pdf",
                mime="application/pdf",
                type="primary"
            )
            st.write(f"Showing **{len(display_records)}** record(s) for selected filter.")
            st.divider()
            
            for r_id, trans, dec, rat, rsk, created_at in display_records:
                date_str = f" | Date: {created_at}" if created_at else ""
                with st.expander(f"Record #{r_id}{date_str}: {dec[:80]}"):
                    st.write(f"**Decision:** {dec}")
                    st.write(f"**Rationale:** {rat}")
                    st.write(f"**Risks:** {rsk}")
                    st.text_area("Original Log", trans, height=100, disabled=True, key=f"raw_{r_id}")
                    
                    ind_pdf = generate_pdf_report([(r_id, trans, dec, rat, rsk, created_at)], report_title=f"Decision #{r_id} Summary")
                    st.download_button(
                        label=f"📄 Download Decision #{r_id} (PDF)",
                        data=ind_pdf,
                        file_name=f"MindGraph_Decision_{r_id}.pdf",
                        mime="application/pdf",
                        key=f"pdf_btn_{r_id}"
                    )
        else:
            st.warning("No decisions found for the selected date/filter criteria.")
    else:
        st.info("Knowledge base is currently empty.")