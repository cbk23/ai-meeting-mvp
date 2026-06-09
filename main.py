import os
import sqlite3
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
from google import genai
import json

app = FastAPI(title="AI Meeting Assistant MVP")

# -------------------------------------------------------------------------
# DATABASE SETUP (SQLite & PostgreSQL Dual Support)
# -------------------------------------------------------------------------
DATABASE = os.getenv("DATABASE_URL", "meetings.db")

def is_postgres():
    """Check if the database URL points to PostgreSQL"""
    return DATABASE.startswith("postgres://") or DATABASE.startswith("postgresql://")

def get_db():
    """Get database connection based on DB type"""
    if is_postgres():
        import psycopg2
        from psycopg2.extras import DictCursor
        conn_str = DATABASE
        # Fix for platforms that provide 'postgres://' connection strings
        if conn_str.startswith("postgres://"):
            conn_str = conn_str.replace("postgres://", "postgresql://", 1)
        
        # Enable SSL for secure production connection (e.g., Supabase)
        if "sslmode" not in conn_str and "localhost" not in conn_str and "127.0.0.1" not in conn_str:
            if "?" in conn_str:
                conn_str += "&sslmode=require"
            else:
                conn_str += "?sslmode=require"
                
        conn = psycopg2.connect(conn_str, cursor_factory=DictCursor)
        return conn
    else:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn

def prepare_query(query: str) -> str:
    """Replace ? placeholders with %s if using PostgreSQL"""
    if is_postgres():
        return query.replace("?", "%s")
    return query

def init_db():
    """Initialize database schema"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(prepare_query('''
        CREATE TABLE IF NOT EXISTS meetings (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            folder TEXT NOT NULL,
            transcript TEXT NOT NULL,
            ai_summary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    '''))
    
    # Check if table is empty and seed with demo data
    cursor.execute('SELECT COUNT(*) FROM meetings')
    if cursor.fetchone()[0] == 0:
        cursor.execute(prepare_query('''
            INSERT INTO meetings (id, title, folder, transcript, ai_summary) VALUES
            (?, ?, ?, ?, ?)
        '''), (
            "1",
            "Q3 Roadmap Alignment",
            "Engineering",
            "John: We need to ship the shared folders feature by June. Sarah: Multi-language support is lagging because of the translation API. John: Let's prioritize folders first, then multi-language.",
            "### AI Meeting Notes\n* **Key Topic:** Q3 Feature Prioritization\n* **Decision:** Shared folders prioritized over multi-language support.\n* **Action Item:** John to oversee folder deployment timeline by June."
        ))
        cursor.execute(prepare_query('''
            INSERT INTO meetings (id, title, folder, transcript, ai_summary) VALUES
            (?, ?, ?, ?, ?)
        '''), (
            "2",
            "Marketing Sync & Budget",
            "Marketing",
            "Alice: The ad spend for May is trending at $5,000. Bob: We should increase it if the conversion rate stays above 3%. Alice: Agreed, let's review next Tuesday.",
            "### AI Meeting Notes\n* **Key Topic:** May Ad Spend\n* **Decision:** Conditionally increase budget if conversions hold above 3%.\n* **Action Item:** Alice and Bob to sync next Tuesday."
        ))
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

folders = ["Engineering", "Marketing", "General"]

# -------------------------------------------------------------------------
# DATA MODELS
# -------------------------------------------------------------------------
class ProcessMeetingRequest(BaseModel):
    title: str
    folder: str
    transcript: str
    template: str

class ChatRequest(BaseModel):
    question: str
    scope: str
    current_meeting_id: Optional[str] = None

# -------------------------------------------------------------------------
# HELPER FUNCTIONS
# -------------------------------------------------------------------------
def get_all_meetings():
    """Fetch all meetings from database"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(prepare_query('SELECT * FROM meetings ORDER BY created_at DESC LIMIT 5'))
    meetings = []
    for row in cursor.fetchall():
        meetings.append({
            "id": row["id"],
            "title": row["title"],
            "folder": row["folder"],
            "transcript": row["transcript"],
            "ai_summary": row["ai_summary"]
        })
    conn.close()
    return meetings

def get_meeting_by_id(meeting_id: str):
    """Fetch a specific meeting"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(prepare_query('SELECT * FROM meetings WHERE id = ?'), (meeting_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "id": row["id"],
            "title": row["title"],
            "folder": row["folder"],
            "transcript": row["transcript"],
            "ai_summary": row["ai_summary"]
        }
    return None

def save_meeting(meeting_id: str, title: str, folder: str, transcript: str, ai_summary: str):
    """Save a new meeting to database"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(prepare_query('''
        INSERT INTO meetings (id, title, folder, transcript, ai_summary)
        VALUES (?, ?, ?, ?, ?)
    '''), (meeting_id, title, folder, transcript, ai_summary))
    conn.commit()
    conn.close()

# -------------------------------------------------------------------------
# API ENDPOINTS
# -------------------------------------------------------------------------

@app.get("/api/dashboard")
def get_dashboard():
    """Get dashboard data: folders and recent meetings"""
    return {
        "folders": folders,
        "meetings": get_all_meetings()
    }

@app.post("/api/notes/generate")
def generate_notes(payload: ProcessMeetingRequest):
    """Generate AI notes from transcript"""
    templates = {
        "standard": "Provide a clean summary, key decisions, and clear bulleted action items.",
        "agile": "Format as an Agile Standup summary: What was accomplished, blockers identified, and next sprint goals.",
        "executive": "Provide a high-level executive summary, financial implications, and strategic next steps."
    }
   
    prompt = f"You are an advanced AI scribe. Analyze the following meeting transcript.\n\nTemplate Requirement: {templates.get(payload.template, templates['standard'])}\n\nTranscript:\n\"\"\"{payload.transcript}\"\"\""
   
    api_key = os.environ.get("GEMINI_API_KEY")
   
    if not api_key or api_key.strip() == "" or "your-gemini-api-key" in api_key:
        ai_notes = f"### [DEMO MODE] AI Summary ({payload.template.upper()})\n\nProcessed transcript for '{payload.title}' successfully!\n\n**Note:** Set your GEMINI_API_KEY environment variable to enable real AI analysis."
    else:
        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            ai_notes = response.text
        except Exception as e:
            print(f"\n{'='*50}\n🚨 GEMINI API ERROR:\n{str(e)}\n{'='*50}\n")
            raise HTTPException(status_code=500, detail=f"Gemini API Error: {str(e)}")
           
    # Generate unique ID
    import time
    new_id = str(int(time.time()))
    
    new_meeting = {
        "id": new_id,
        "title": payload.title,
        "folder": payload.folder,
        "transcript": payload.transcript,
        "ai_summary": ai_notes
    }
    
    # Save to database
    save_meeting(new_id, payload.title, payload.folder, payload.transcript, ai_notes)
    
    return new_meeting

@app.post("/api/chat")
def chat_with_context(payload: ChatRequest):
    """Chat with AI about meetings"""
    meetings = get_all_meetings()
    
    if payload.scope == "all":
        context = "\n".join([f"Meeting '{m['title']}': {m['transcript']}" for m in meetings])
    else:
        target = get_meeting_by_id(payload.current_meeting_id) if payload.current_meeting_id else None
        context = target["transcript"] if target else "No meeting selected."

    prompt = f"Answer the user query based ONLY on the provided meeting context below. If the information isn't present, state politely that it wasn't discussed.\n\nContext:\n\"\"\"{context}\"\"\"\n\nQuery: {payload.question}"
   
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key or api_key.strip() == "" or "your-gemini-api-key" in api_key:
        return {"answer": "[DEMO MODE] Set your GEMINI_API_KEY environment variable to enable AI responses."}
   
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return {"answer": response.text}
    except Exception as e:
        print(f"\n{'='*50}\n🚨 GEMINI CHAT ERROR:\n{str(e)}\n{'='*50}\n")
        return {"answer": f"Error communicating with AI: {str(e)}"}

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    """Serve the main UI"""
    with open("templates.html", "r") as f:
        return f.read()

# Health check endpoint (useful for deployment monitoring)
@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "AI Meeting Assistant MVP"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
