import os
import json
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from google import genai
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# 1. Database Setup (SQLite)
DATABASE_URL = "sqlite:///./mindgraph.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class KnowledgeRecord(Base):
    __tablename__ = "knowledge_records"

    id = Column(Integer, primary_key=True, index=True)
    channel_name = Column(String, index=True)
    transcript = Column(Text)
    extracted_json = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# 2. Semantic Search Embedding Model Initialization
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# 3. FastAPI Setup
app = FastAPI(title="MindGraph AI - Tacit Knowledge Extractor")

import os

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ConversationInput(BaseModel):
    channel_name: str
    chat_transcript: str

class DecisionResponse(BaseModel):
    status: str
    record_id: int
    extracted_data: dict

class SearchQuery(BaseModel):
    query: str

@app.get("/")
def home():
    return {"message": "MindGraph AI Core Engine is Running!"}

@app.post("/extract-decision", response_model=DecisionResponse)
def extract_decision(data: ConversationInput, db: Session = Depends(get_db)):
    prompt = f"""
    You are an Enterprise Institutional Knowledge Extractor.
    Analyze the following team discussion transcript from channel #{data.channel_name}.
    
    Extract:
    1. Key Decisions Made
    2. Rationale/Reasoning behind each decision (The "WHY")
    3. Technical or Business Risks identified

    Chat Transcript:
    {data.chat_transcript}

    Return response in clear raw JSON format with keys: 'decisions', 'rationale', 'risks'.
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        raw_text = response.text.replace("```json", "").replace("```", "").strip()
        parsed_json = json.loads(raw_text)

        # Save to Database
        db_record = KnowledgeRecord(
            channel_name=data.channel_name,
            transcript=data.chat_transcript,
            extracted_json=json.dumps(parsed_json)
        )
        db.add(db_record)
        db.commit()
        db.refresh(db_record)

        return {"status": "success", "record_id": db_record.id, "extracted_data": parsed_json}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/records")
def fetch_all_records(db: Session = Depends(get_db)):
    records = db.query(KnowledgeRecord).all()
    return records

@app.post("/search-knowledge")
def search_knowledge(search_data: SearchQuery, db: Session = Depends(get_db)):
    records = db.query(KnowledgeRecord).all()
    if not records:
        return {"query": search_data.query, "results": [], "summary": "No records found in database."}

    # Generate query vector
    query_vec = embedding_model.encode([search_data.query])

    # Generate document vectors from extracted data
    doc_texts = [r.extracted_json for r in records]
    doc_vecs = embedding_model.encode(doc_texts)

    # Compute similarity
    similarities = cosine_similarity(query_vec, doc_vecs)[0]
    
    # Sort top matching records
    top_indices = np.argsort(similarities)[::-1][:3]
    
    matched_records = []
    retrieved_context = ""
    for idx in top_indices:
        rec = records[idx]
        score = float(similarities[idx])
        if score > 0.1:  # Relevance threshold
            matched_records.append({
                "record_id": rec.id,
                "channel_name": rec.channel_name,
                "relevance_score": round(score, 3),
                "extracted_data": json.loads(rec.extracted_json)
            })
            retrieved_context += f"\n- Channel #{rec.channel_name}: {rec.extracted_json}"

    # Generate AI Answer using RAG context
    rag_prompt = f"""
    You are an AI Organizational Memory Assistant.
    Answer the user's question accurately using ONLY the retrieved organizational decisions context below.

    User Question: {search_data.query}

    Retrieved Context from Database:
    {retrieved_context if retrieved_context else "No relevant context found."}

    Be concise, direct, and highlight decisions, rationale, or risks clearly.
    """

    ai_answer = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=rag_prompt
    ).text

    return {
        "query": search_data.query,
        "ai_answer": ai_answer,
        "matched_records": matched_records
    }