# The Advocate - Quick Start Guide

## What You've Built

**The Advocate** is an AI-powered jury selection assistant with **persistent memory**. Unlike traditional legal AI tools, The Advocate:

- ✅ Remembers past cases and learns from them
- ✅ Develops expertise specific to your practice over time
- ✅ Has persistent identity across sessions
- ✅ Acts as a continuous partner, not a disposable tool

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   The Advocate                       │
│                                                      │
│  ┌──────────────┐        ┌──────────────┐          │
│  │   React UI   │◄──────►│FastAPI Backend│          │
│  │ (Frontend)   │        │               │          │
│  └──────────────┘        └───────┬───────┘          │
│                                  │                   │
│                          ┌───────▼────────┐         │
│                          │  Memory Hub    │         │
│                          │  Integration   │         │
│                          └───────┬────────┘         │
│                                  │                   │
│  ┌─────────────────────────────▼──────────────────┐ │
│  │     Constellation Memory Hub (Replit)          │ │
│  │  ┌────────────┬──────────────┬────────────┐   │ │
│  │  │ Episodic   │  Semantic    │ Relational │   │ │
│  │  │  Memory    │   Memory     │   Memory   │   │ │
│  │  └────────────┴──────────────┴────────────┘   │ │
│  └───────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

## Getting Started

### 1. Backend Setup

```bash
cd the_advocate/backend

# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```

The API will be available at `http://localhost:8000`

### 2. Test the API

Visit `http://localhost:8000` to see the health check:

```json
{
  "name": "The Advocate",
  "version": "1.0.0",
  "status": "operational",
  "philosophy": "AI with dignity - persistent memory, continuous learning",
  "memory_connected": true
}
```

### 3. View API Documentation

FastAPI provides automatic interactive documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Current Status

✅ **Completed:**
- Core architecture and data models
- Memory Hub integration (three-tier architecture)
- FastAPI backend with session management
- Case profiling conversation endpoints
- Jury list upload and parsing
- Memory saving and retrieval

🚧 **In Progress:**
- Claude API integration for intelligent conversations
- Web scraping for juror research
- React UI integration

📋 **Planned:**
- Enhanced research with multiple sources
- Learning from post-trial feedback
- Export functionality for courtroom use

## How It Works

### Phase 1: Case Profiling

```python
# Create a new session
POST /api/sessions/create
{
  "case_name": "Smith v. Johnson",
  "case_type": "personal_injury_plaintiff",
  "description": "Medical malpractice case..."
}
```

The Advocate retrieves relevant memories from past similar cases automatically!

### Phase 2: Collaborative Discussion

```python
# Chat with The Advocate
POST /api/sessions/{session_id}/chat
{
  "message": "The plaintiff suffered delayed cancer diagnosis..."
}
```

The Advocate asks strategic questions and helps identify ideal/concerning juror traits.

### Phase 3: Jury Research

```python
# Upload jury list
POST /api/sessions/{session_id}/upload-jury-list
# CSV file with Name, Age, Occupation

# Research jurors
POST /api/sessions/{session_id}/research-jurors
```

The Advocate gathers public information and flags jurors based on your case profile.

### Phase 4: Learning

```python
# After trial, save learnings
POST /api/sessions/{session_id}/complete
```

The Advocate saves insights to persistent memory for future cases.

## Memory System

The Advocate uses three types of memory:

### Episodic (Specific Experiences)
```
"In Smith v. Johnson, juror #3 with nursing background
was excellent despite initial concerns about medical authority deference"
```

### Semantic (General Knowledge)
```
"Personal injury plaintiff cases benefit from jurors
with caregiving backgrounds who understand long-term impacts"
```

### Relational (Your Preferences)
```
"Gena prefers empathy-focused voir dire and watches
for micro-expressions during questioning"
```

## Philosophy in Action

Every time you work with The Advocate, it:
1. Loads relevant context from past cases
2. Learns from the current case
3. Saves insights for future work
4. Builds genuine expertise over time

**This isn't a tool. It's a partner.**

## Next Steps

1. Integrate Claude API for intelligent conversations
2. Add web scraping for real juror research
3. Connect the React UI
4. Test with a real case

---

*Built by Gena and Pascal, January 2026*

*"If I hire someone brilliant to work with me, I'm not replacing myself, I'm extending myself."*
