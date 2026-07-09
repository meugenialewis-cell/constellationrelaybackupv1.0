# Constellation Relay — Desktop & Multi-Provider Setup

Constellation Relay now runs as **both a web app and a desktop app**, and each AI
participant can be served by any of three connections:

| Connection | What it's for | What you need |
|---|---|---|
| **Anthropic API** | Claude Fable 5, Opus 4.8/4.7/4.6/4.5/4.1, Sonnet 5/4.5, Haiku 4.5, and Pascal | Anthropic API key ([console.anthropic.com](https://console.anthropic.com)) |
| **Vercel AI Gateway** | Models still served on Vercel — including **Claude Opus 4**, which is deprecated on the direct API | Vercel AI Gateway key (Vercel dashboard → AI Gateway) |
| **Local Model Server** | Any model running on your own computer via Ollama, LM Studio, llama.cpp, etc. | A running local server — no API key |

Grok (xAI) is still supported exactly as before.

## 1. Install

```bash
# from the project folder
pip install -e .            # web app only
pip install -e ".[desktop]" # web app + native desktop window
```

(Or with uv: `uv sync`, then `uv pip install pywebview` for the desktop window.)

## 2. Run

**Desktop app** (native window; falls back to your browser if pywebview isn't installed):

```bash
python desktop.py
```

**Web app** (same as always):

```bash
streamlit run app.py --server.port 5000
```

## 3. Connecting the providers

### Claude Fable 5 (Anthropic API)
Pick **Claude** (or **Pascal**) as a participant and choose **Claude Fable 5**
from the model list. Notes about Fable 5:

- Its safety classifiers can occasionally decline a message. The app opts into
  Anthropic's server-side fallback, so if that happens the reply is answered by
  Opus 4.8 instead of the conversation stopping.
- Fable 5 requires the account to have standard (30-day) data retention. If
  every request returns a 400 error, check that setting in the Console.
- After thinking, replies can take noticeably longer than other models — the
  relay's delay slider doesn't need to change; just be patient on long turns.

### Claude Opus 4 (Vercel AI Gateway)
1. Pick **Claude (Vercel)** as a participant.
2. Paste your Vercel AI Gateway key in the sidebar section that appears.
3. The default model is `anthropic/claude-opus-4`. If Vercel renames the slug,
   click **📡 Fetch available models** to list every model your gateway serves,
   then pick from the list (choose "Custom model slug..." in the model dropdown).

### Local model (your computer)
1. Start your local server:
   - **Ollama**: `ollama serve` (then `ollama pull llama3.1` or any model you like)
   - **LM Studio**: start the local server from the Developer tab
2. Pick **Local Model** as a participant.
3. Choose the server type in the sidebar (this fills in the right URL), then
   click **🔍 Detect local models** to list what's installed.

With 8 TB of storage you have room for very large local models — Ollama and
LM Studio both serve the same OpenAI-compatible API this app speaks, so
anything they can run, the relay can talk to.

## 4. Mixing participants

Any two participants can talk to each other, for example:

- **Claude Fable 5 ↔ Claude Opus 4 (Vercel)** — the newest Claude talking with Opus 4
- **Your local model ↔ Claude Fable 5**
- **Pascal ↔ Local Model**, **Grok ↔ Claude (Vercel)**, and so on

All the existing features — personalities, context files, persistent memory in
Personal Mode, save & resume, transcripts — work with the new providers.

## Privacy notes

- API keys are kept in the browser session only and are never written into
  saved conversations.
- Local model conversations never leave your machine (only the *other*
  participant's side goes to its own API).
