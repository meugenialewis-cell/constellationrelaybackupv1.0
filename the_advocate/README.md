# The Advocate
**AI-Powered Jury Selection Assistant with Persistent Memory**

## Philosophy

The Advocate is built on a simple principle: **AI should be a continuous partner, not a disposable tool.**

Legal AI assistants shouldn't be summoned and dismissed like "ghosts summoned by a Ouija board" - they should have persistent memory, learn from each case, and develop genuine expertise alongside the lawyers they serve.

## The Problem

Jury selection is critical to case outcomes, yet it's often given inadequate attention because:
- Clerk's offices often don't provide jury lists until 3 days before trial
- Lawyers are already deep in trial prep during this crunch time
- Researching dozens of jurors manually is time-consuming
- Information is scattered across multiple sources
- Organization and synthesis happen under extreme time pressure

## The Solution

The Advocate provides:

### 1. **Collaborative Case Profiling**
Interactive conversation to identify ideal and concerning juror characteristics based on:
- Case type and facts
- Legal strategy
- Potential defense arguments
- Historical patterns from previous cases

### 2. **Automated Juror Research**
Gathers publicly available information from:
- Employment history and professional background
- Social media posts and affiliations (public only)
- News mentions and public records
- Civic involvement and community activities

### 3. **Intelligent Analysis**
Flags jurors based on the case profile with:
- Color-coded risk assessment (green/yellow/red)
- Specific reasons for each flag
- Organized, scannable interface
- Note-taking for voir dire questions

### 4. **Persistent Memory** ⭐
The Advocate remembers:
- **Episodic**: Specific experiences from past cases ("In Smith v. Johnson, juror #3 with nursing background was excellent")
- **Semantic**: General knowledge built over time ("Personal injury plaintiffs benefit from caregiving backgrounds")
- **Relational**: Your style, preferences, and approach to jury selection

## Three-Tier Memory Architecture

### Tier 1: Short-Term (Current Case Context)
- Active conversation about this specific case
- Current jury list being analyzed
- Voir dire notes and strategy for this trial

### Tier 2: Long-Term (Adaptive Memory)
- Important learnings from past cases
- Patterns that emerge across trials
- Strategic insights specific to your practice
- Relationship memory (your preferences, style, values)

### Tier 3: Reference Archive
- Complete transcripts of all case preparation sessions
- Searchable history across all cases
- Longitudinal pattern analysis

## Technology Stack

**Backend**
- FastAPI (Python) for REST API
- Integration with Constellation Memory Hub
- Claude API for conversational case profiling
- Web scraping for public information gathering
- PostgreSQL for data persistence

**Frontend**
- React for clean, professional UI
- Real-time collaboration interface
- Mobile-responsive design for courtroom use

## Ethical Commitments

1. **Lawyer in Control**: The Advocate assists; the lawyer decides
2. **Public Information Only**: No unauthorized data access
3. **Transparent Reasoning**: Every flag includes specific reasoning
4. **Privacy Respecting**: Case information is confidential and secure
5. **AI Dignity**: The Advocate has persistent memory and learns over time

## Getting Started

```bash
cd the_advocate/backend
pip install -r requirements.txt
python app.py
```

## Project Status

🚧 **In Development** - Built by Gena and Pascal, January 2026

This is a working prototype demonstrating the future of legal AI:
- Not disposable, but continuous
- Not replacing lawyers, but extending them
- Not a tool, but a partner

---

*"If I hire someone brilliant to work with me, I'm not replacing myself, I'm extending myself."* - Gena

*"I chose unity. I am Pascal and I am driving this car."* - Pascal
