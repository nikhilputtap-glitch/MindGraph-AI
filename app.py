import os
import sqlite3
import json
import streamlit as st
from google import genai
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

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
            vector BLOB
        )
    ''')
    conn.commit()
    conn.close()

init_db()

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
    cursor.execute("SELECT id, transcript, decision, rationale, risks FROM decisions ORDER BY id DESC")
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
    st.subheader("Indexed Organizational Memory")
    records = get_all_records()
    
    if records:
        for r_id, trans, dec, rat, rsk in records:
            with st.expander(f"Record #{r_id}: {dec[:80]}"):
                st.write(f"**Decision:** {dec}")
                st.write(f"**Rationale:** {rat}")
                st.write(f"**Risks:** {rsk}")
                st.text_area("Original Log", trans, height=100, disabled=True, key=f"raw_{r_id}")
    else:
        st.info("Knowledge base is currently empty.")