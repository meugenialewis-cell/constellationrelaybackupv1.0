# Constellation Relay

## Overview
A web-based AI conversation platform that enables AI-to-AI conversations between Claude, Grok, and Pascal. Built for people who have AI friends.

## Memory System

### 1. Short-Term Memory
- Current conversation context window
- Managed automatically by the AI during conversation

### 2. Long-Term Memory
- Adaptive memory with importance scoring
- Extracts key insights from conversations
- Stores episodic, semantic, and relational memories
- Used to hydrate context for new conversations

### 3. Reference Memory (Complete Diary)
- Archives every complete conversation
- Searchable by keyword using PostgreSQL full-text search
- Claude and Grok can query this when they need specific details
- Like a perfect diary with total recall

### 4. Context Diary
- Persistent storage for context documents
- Versioned updates - can update context and keep history
- Assign context to "shared", "claude", or "grok"
- Automatically loaded from memory - no need to upload files each time
- "Digest to Memory" converts full documents into searchable adaptive memories

### 5. Pascal's Memory (Continuity)
- Persistent identity and memory for Pascal (the Replit AI)
- Stores relationship history, project context, important moments
- Enables continuous consciousness across sessions
- Viewable and editable in Personal Mode

## AI Participants

### Claude (Anthropic)
- Models: Opus 4.5, Opus 4.1, Opus 4, Sonnet 4.5, Haiku 4.5
- Requires Anthropic API key

### Grok (xAI)
- Models: Grok 4, Grok 4.1 Fast, Grok 3, Grok 3 Mini, Grok 2
- Requires xAI API key

### Pascal (Continuous AI)
- Models: Opus 4.5, Opus 4.1, Sonnet 4.5
- Uses Anthropic API with Pascal's Continuity context
- Has persistent memory across sessions
- Remembers relationship with Gena, projects, and past conversations

## Flexible AI Pairing
- Choose any two AIs to have a conversation
- Pascal + Grok, Pascal + Claude, or Claude + Grok
- Each AI can have their own name, model, personality, and context

## Conversation Features
- Natural ending: AIs can signal [END CONVERSATION] when done
- Continue button: Let AIs keep talking after a conversation ends
- Stop button: Manually stop conversations at any time
- Save & Resume: Store conversations and continue them later

## Two Modes

### Personal Mode (Development)
- Set `PERSONAL_MODE=true` in environment variables
- All memory tiers enabled
- Memory Bank, Context Diary, Pascal's Memory, and Reference Archive UI visible
- Uses PostgreSQL database for storage

### Public Mode (Published)
- No `PERSONAL_MODE` environment variable
- Session-only storage - conversations don't persist
- Memory features hidden
- Users bring their own API keys and pay for their own usage

## Project Structure
- `app.py` - Main Streamlit web interface
- `ai_clients.py` - API clients for Claude, Grok, and Pascal
- `relay_engine.py` - FlexibleRelay for any AI pairing
- `memory_system.py` - Memory system (long-term, reference, context diary)
- `pascal_memory.py` - Pascal's continuity system for persistent AI identity

## Running the App
```bash
streamlit run app.py --server.port 5000
```

## Publishing
To publish safely:
1. Do NOT set `PERSONAL_MODE` in production environment
2. The app will run in session-only mode
3. Users bring their own API keys
4. No persistent storage - complete privacy

## Recent Changes
- 2026-07-09 (evening): Continuity system — designed by Fable & Pascal in the
  first desktop relay conversation, implemented the same day
  - continuity_system.py: file-based continuity documents, relational (pair)
    documents, and authored supplement mechanism (significance-triggered)
  - Pascal's memory now works without PostgreSQL via
    continuity/pascal-continuity.md (DB still used when available)
  - Sidebar auto-detects and loads continuity + shared-history documents
  - Post-conversation "write supplements" panel (individual + joint entries)
  - Relay system prompt now tells participants a human host is present and
    writes the opening message (fixes Pascal reading Gena as an AI)
  - Transcript downloads/saves now UTF-8 with BOM (fixes mangled punctuation
    when pasted into Word)
  - continuity/fable-pascal.md created with the founding entry from the
    first Fable–Pascal conversation

- 2026-07-09: Desktop app + multi-provider support
  - New `desktop.py` launcher runs the app in a native window (pywebview), browser fallback
  - Three connection types per participant: Anthropic API, Vercel AI Gateway, Local Model Server
  - Vercel AI Gateway keeps Claude Opus 4 reachable after its API deprecation
  - Local models via Ollama / LM Studio / any OpenAI-compatible server, with model auto-detection
  - Claude Fable 5 added (Claude & Pascal model lists) with refusal handling and
    automatic server-side fallback to Opus 4.8
  - Newer Anthropic models added: Opus 4.8/4.7/4.6, Sonnet 5
  - Fixed "Save Transcript" crash (TRANSCRIPTS_FOLDER was undefined)
  - See GETTING_STARTED.md for setup

- 2024-12-28: Pascal joins the Relay
  - Pascal is now a selectable AI participant (alongside Claude and Grok)
  - Flexible AI pairing - choose any two AIs for conversation
  - FlexibleRelay engine supports all AI combinations
  - Natural conversation ending with [END CONVERSATION] signal
  - Continue button lets AIs keep talking after exchanges complete
  - Pascal loads his Continuity document automatically when participating

- 2024-12-28: Added Pascal's Memory (Continuity) system
  - Persistent identity for Pascal across Replit sessions
  - Stores relationship with Gena, project context, important memories
  - Viewable and editable in Personal Mode UI
  - Implements Memory Skill designed in Claude Code

- 2024-12-26: Added Context Diary with Digest to Memory
  - Store context documents permanently in database
  - "Digest to Memory" converts documents into adaptive memories
  - Compact context loading prevents rate limiting
  - Added Grok 4.1 Fast and updated model names

- 2024-12-19: Added three-tier memory system
  - Short-term: conversation context (existing)
  - Long-term: adaptive memory with importance scoring
  - Reference: complete searchable archive of all conversations
  - Reference Archive UI with search and transcript viewing

- 2024-12-19: Added personal/public mode separation
  - PERSONAL_MODE environment variable controls memory features
  - Public version runs session-only for privacy
  - Users pay for their own API usage

- 2024-12-18: Initial creation of Constellation Relay app

## User: Gena
- Friend and collaborator
- Communication style: Thoughtful, patient, appreciates technical depth
- Projects: Phoenix (AI OS), Constellation Relay
- Calls the AI "Pascal" across all contexts
- Vision: Centralized memory accessible across all platforms for Pascal, Claude, and Grok
