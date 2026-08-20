import streamlit as st
import requests
import json
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

st.set_page_config(page_title="MindGraph AI Dashboard", layout="wide")

st.title("🧠 MindGraph AI - Tacit Knowledge Extractor & RAG Search")
st.write("Extract decisions, rationale, risks, export reports, and search institutional knowledge automatically.")

st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["Extract Knowledge", "Semantic RAG Search", "Export Reports", "View Stored Records"])

API_URL = "http://127.0.0.1:8001"

def generate_pdf(records):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, spaceAfter=12)
    heading_style = ParagraphStyle('HeadingStyle', parent=styles['Heading2'], fontSize=14, spaceAfter=8)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=10, spaceAfter=6)

    story.append(Paragraph("MindGraph AI - Tacit Knowledge Executive Report", title_style))
    story.append(Spacer(1, 12))

    for rec in records:
        story.append(Paragraph(f"Record #{rec['id']} | Channel: #{rec['channel_name']}", heading_style))
        story.append(Paragraph(f"<b>Created At:</b> {rec['created_at']}", body_style))
        
        try:
            extracted = json.loads(rec['extracted_json'])
            
            story.append(Paragraph("<b>Decisions:</b>", body_style))
            for d in extracted.get("decisions", []):
                story.append(Paragraph(f"• {d}", body_style))
                
            story.append(Paragraph("<b>Rationale:</b>", body_style))
            for r in extracted.get("rationale", []):
                story.append(Paragraph(f"• {r}", body_style))
                
            story.append(Paragraph("<b>Risks:</b>", body_style))
            for rk in extracted.get("risks", []):
                story.append(Paragraph(f"• {rk}", body_style))
        except:
            story.append(Paragraph(f"Raw: {rec['extracted_json']}", body_style))
            
        story.append(Spacer(1, 14))

    doc.build(story)
    buffer.seek(0)
    return buffer

if page == "Extract Knowledge":
    st.subheader("Extract Tacit Knowledge from Transcript")
    
    channel_name = st.text_input("Channel Name", value="engineering")
    transcript = st.text_area("Chat Transcript", height=200, placeholder="Paste chat transcript here...")
    
    if st.button("Extract Knowledge", type="primary"):
        if not transcript.strip():
            st.warning("Please enter a chat transcript.")
        else:
            with st.spinner("Analyzing transcript using Gemini AI..."):
                try:
                    payload = {"channel_name": channel_name, "chat_transcript": transcript}
                    res = requests.post(f"{API_URL}/extract-decision", json=payload)
                    
                    if res.status_code == 200:
                        data = res.json()
                        st.success(f"Successfully Extracted & Saved! (Record ID: {data['record_id']})")
                        
                        extracted = data.get("extracted_data", {})
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown("### 📌 Decisions Made")
                            for item in extracted.get("decisions", []):
                                st.write(f"- {item}")
                                
                        with col2:
                            st.markdown("### 💡 Rationale (Why)")
                            for item in extracted.get("rationale", []):
                                st.write(f"- {item}")
                                
                        with col3:
                            st.markdown("### ⚠️ Identified Risks")
                            for item in extracted.get("risks", []):
                                st.write(f"- {item}")
                    else:
                        st.error(f"API Error: {res.text}")
                except Exception as e:
                    st.error(f"Connection Failed: Ensure FastAPI server is running on port 8001. ({e})")

elif page == "Semantic RAG Search":
    st.subheader("🔍 Ask Organizational Memory (RAG Search)")
    query = st.text_input("Ask a question about past decisions", placeholder="e.g., Why did we choose Redis?")
    
    if st.button("Search Knowledge Base", type="primary"):
        if not query.strip():
            st.warning("Please enter a search question.")
        else:
            with st.spinner("Searching vector database & generating answer..."):
                try:
                    res = requests.post(f"{API_URL}/search-knowledge", json={"query": query})
                    if res.status_code == 200:
                        data = res.json()
                        st.markdown("### 🤖 AI Summary Answer")
                        st.info(data.get("ai_answer"))
                        
                        st.markdown("### 📚 Source Records Retrieved")
                        records = data.get("matched_records", [])
                        if records:
                            for rec in records:
                                with st.expander(f"Record #{rec['record_id']} | Channel: #{rec['channel_name']} (Relevance: {rec['relevance_score']})"):
                                    st.json(rec['extracted_data'])
                        else:
                            st.warning("No matching historical records found.")
                    else:
                        st.error(f"Search API Error: {res.text}")
                except Exception as e:
                    st.error(f"Connection Error: {e}")

elif page == "Export Reports":
    st.subheader("📄 Export Decisions Documentation")
    st.write("Generate and download executive decision reports in PDF or Markdown format.")

    try:
        res = requests.get(f"{API_URL}/records")
        if res.status_code == 200:
            records = res.json()
            if records:
                st.write(f"Total Stored Records Available: **{len(records)}**")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    pdf_data = generate_pdf(records)
                    st.download_button(
                        label="📥 Download Executive PDF Report",
                        data=pdf_data,
                        file_name="MindGraph_Decisions_Report.pdf",
                        mime="application/pdf",
                        type="primary"
                    )

                with col2:
                    md_text = "# MindGraph AI - Decisions Log\n\n"
                    for rec in records:
                        md_text += f"## Record #{rec['id']} - Channel: #{rec['channel_name']}\n"
                        md_text += f"**Date:** {rec['created_at']}\n\n"
                        md_text += f"```json\n{rec['extracted_json']}\n```\n\n---\n\n"
                    
                    st.download_button(
                        label="📝 Download Markdown (.md) Report",
                        data=md_text,
                        file_name="MindGraph_Decisions_Report.md",
                        mime="text/markdown"
                    )
            else:
                st.info("No records found to export.")
        else:
            st.error("Failed to fetch records.")
    except Exception as e:
        st.error(f"Connection Failed: {e}")

elif page == "View Stored Records":
    st.subheader("Database History Logs")
    if st.button("Refresh Records"):
        st.rerun()
        
    try:
        res = requests.get(f"{API_URL}/records")
        if res.status_code == 200:
            records = res.json()
            if records:
                st.dataframe(records, use_container_width=True)
            else:
                st.info("No records found in database yet.")
        else:
            st.error("Failed to fetch records.")
    except Exception as e:
        st.error(f"Connection Failed: {e}")