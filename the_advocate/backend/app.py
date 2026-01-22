"""
The Advocate - AI-Powered Jury Selection Assistant
FastAPI Backend with Persistent Memory
"""

import os
from typing import List, Optional
from datetime import datetime
import uuid

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from models import (
    CaseProfile,
    CaseSession,
    ChatMessage,
    Juror,
    JuryList,
    CaseType,
    MemoryType
)
from memory_client import get_memory_client

# Initialize FastAPI app
app = FastAPI(
    title="The Advocate",
    description="AI-Powered Jury Selection Assistant with Persistent Memory",
    version="1.0.0"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for active sessions (will move to database later)
active_sessions: dict[str, CaseSession] = {}

# Memory client
memory = get_memory_client()


# ============================================================================
# Request/Response Models
# ============================================================================

class CaseProfileRequest(BaseModel):
    """Request to create a new case profile"""
    case_name: str
    case_type: CaseType
    description: str


class ChatRequest(BaseModel):
    """Request to send a message in case profiling"""
    session_id: str
    message: str


class ChatResponse(BaseModel):
    """Response from case profiling conversation"""
    role: str
    content: str
    timestamp: datetime


class JurorResearchRequest(BaseModel):
    """Request to research jurors from uploaded list"""
    session_id: str
    juror_names: List[str]


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Health check and API info"""
    return {
        "name": "The Advocate",
        "version": "1.0.0",
        "status": "operational",
        "philosophy": "AI with dignity - persistent memory, continuous learning",
        "memory_connected": True
    }


@app.post("/api/sessions/create", response_model=CaseSession)
async def create_session(request: CaseProfileRequest):
    """
    Create a new case session with profile
    Retrieves relevant memories from past cases
    """
    session_id = str(uuid.uuid4())

    # Create case profile
    case_profile = CaseProfile(
        id=str(uuid.uuid4()),
        case_name=request.case_name,
        case_type=request.case_type,
        description=request.description
    )

    # Get relevant context from memory
    context = memory.get_context_for_case(
        case_type=request.case_type.value,
        case_description=request.description
    )

    # Create initial conversation with context
    initial_messages = [
        ChatMessage(
            role="assistant",
            content=f"Hello! I'm The Advocate, and I'm here to help you prepare for jury selection in {request.case_name}."
        )
    ]

    # Add context from memory if available
    if context:
        initial_messages.append(
            ChatMessage(
                role="assistant",
                content=f"Based on my experience with similar cases, here's what I remember that might be relevant:\n\n{context}\n\nNow, let's discuss your specific case. What are the key facts the jury will hear?"
            )
        )
    else:
        initial_messages.append(
            ChatMessage(
                role="assistant",
                content="This appears to be a new type of case for me. Let's build the juror profile together. What are the key facts the jury will hear?"
            )
        )

    # Create session
    session = CaseSession(
        id=session_id,
        case_profile=case_profile,
        conversation_history=initial_messages
    )

    active_sessions[session_id] = session

    return session


@app.get("/api/sessions/{session_id}", response_model=CaseSession)
async def get_session(session_id: str):
    """Get an existing case session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    return active_sessions[session_id]


@app.post("/api/sessions/{session_id}/chat", response_model=ChatResponse)
async def chat_with_advocate(session_id: str, request: ChatRequest):
    """
    Send a message in case profiling conversation
    The Advocate responds with strategic questions and suggestions
    """
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = active_sessions[session_id]

    # Add user message to history
    user_message = ChatMessage(
        role="user",
        content=request.message
    )
    session.conversation_history.append(user_message)

    # Generate response (simplified for now - will integrate Claude API later)
    response_content = generate_advocate_response(
        session.case_profile,
        session.conversation_history
    )

    assistant_message = ChatMessage(
        role="assistant",
        content=response_content
    )
    session.conversation_history.append(assistant_message)

    session.updated_at = datetime.utcnow()

    return assistant_message


@app.post("/api/sessions/{session_id}/upload-jury-list")
async def upload_jury_list(
    session_id: str,
    file: UploadFile = File(...)
):
    """
    Upload jury list CSV and initiate research
    """
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = active_sessions[session_id]

    # Read CSV content
    content = await file.read()
    csv_text = content.decode('utf-8')

    # Parse CSV and create jurors
    jurors = parse_jury_list_csv(csv_text)

    # Create jury list
    jury_list = JuryList(
        id=str(uuid.uuid4()),
        case_id=session.case_profile.id,
        case_name=session.case_profile.case_name,
        jurors=jurors,
        total_jurors=len(jurors)
    )

    session.jury_list = jury_list
    session.updated_at = datetime.utcnow()

    return {
        "status": "uploaded",
        "total_jurors": len(jurors),
        "message": f"Uploaded {len(jurors)} jurors. Starting research..."
    }


@app.post("/api/sessions/{session_id}/research-jurors")
async def research_jurors(session_id: str):
    """
    Research all jurors in the jury list
    Gathers public information and analyzes based on case profile
    """
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = active_sessions[session_id]

    if not session.jury_list:
        raise HTTPException(status_code=400, detail="No jury list uploaded")

    # Research each juror
    for juror in session.jury_list.jurors:
        # This will be implemented with real web scraping
        # For now, returns placeholder
        research_juror(juror, session.case_profile)

    session.jury_list.researched_count = len(session.jury_list.jurors)
    session.updated_at = datetime.utcnow()

    return {
        "status": "completed",
        "researched": session.jury_list.researched_count,
        "total": session.jury_list.total_jurors
    }


@app.get("/api/sessions/{session_id}/jurors", response_model=List[Juror])
async def get_jurors(session_id: str):
    """Get all jurors for a session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = active_sessions[session_id]

    if not session.jury_list:
        return []

    return session.jury_list.jurors


@app.post("/api/sessions/{session_id}/complete")
async def complete_case(session_id: str):
    """
    Mark case as complete and save learnings to memory
    """
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = active_sessions[session_id]

    # Save key learnings to memory
    learning_summary = f"Completed jury selection for {session.case_profile.case_name} ({session.case_profile.case_type.value})"

    engram_id = memory.save_case_learning(
        learning=learning_summary,
        case_name=session.case_profile.case_name,
        importance=3
    )

    if engram_id:
        session.memory_engrams.append(engram_id)

    return {
        "status": "completed",
        "memory_saved": engram_id is not None,
        "engram_id": engram_id
    }


@app.get("/api/memory/learnings")
async def get_learnings(case_type: Optional[str] = None):
    """Get learnings from past cases"""
    learnings = memory.get_case_learnings(case_type)
    return {
        "count": len(learnings),
        "learnings": learnings
    }


# ============================================================================
# Helper Functions
# ============================================================================

def generate_advocate_response(
    case_profile: CaseProfile,
    conversation_history: List[ChatMessage]
) -> str:
    """
    Generate response from The Advocate
    TODO: Integrate with Claude API for real conversation
    """
    # Simplified response logic for now
    last_user_message = next(
        (msg for msg in reversed(conversation_history) if msg.role == "user"),
        None
    )

    if not last_user_message:
        return "I'm here to help. What would you like to discuss?"

    content = last_user_message.content.lower()

    # Pattern-based responses (will be replaced with Claude API)
    if "personal injury" in content or "plaintiff" in content:
        return "For personal injury plaintiff cases, we typically want jurors who can empathize with long-term impacts while being analytical about damages. What are the specific injuries involved?"

    elif "medical" in content:
        return "Medical cases require jurors who can understand complexity without automatically deferring to medical authority. Are there specific aspects of the medical testimony that might be contentious?"

    elif "defense" in content:
        return "Defense work requires careful attention to burden of proof and reasonable doubt. What's the prosecution's strongest evidence, and where might we find bias in potential jurors?"

    else:
        return "Thank you for that information. To build an effective juror profile, could you tell me more about: 1) Your theory of the case, 2) The defense's likely arguments, and 3) Any hot-button issues that might trigger strong biases?"


def parse_jury_list_csv(csv_content: str) -> List[Juror]:
    """
    Parse CSV content into Juror objects
    Expected format: Name,Age,Occupation
    """
    import csv
    from io import StringIO

    jurors = []
    reader = csv.DictReader(StringIO(csv_content))

    for row in reader:
        juror = Juror(
            id=str(uuid.uuid4()),
            name=row.get('Name', row.get('name', '')),
            age=int(row.get('Age', row.get('age', 0))) if row.get('Age') or row.get('age') else None,
            occupation=row.get('Occupation', row.get('occupation', ''))
        )
        jurors.append(juror)

    return jurors


def research_juror(juror: Juror, case_profile: CaseProfile):
    """
    Research a juror using public information sources
    TODO: Implement real web scraping
    """
    # Placeholder - will be implemented with real research
    juror.researched_at = datetime.utcnow()

    # For now, just mark as researched
    # Real implementation will gather public info and analyze

    return juror


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
