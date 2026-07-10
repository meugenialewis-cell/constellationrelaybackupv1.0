"""The Parlor — one-on-one conversations between Gena and her AI friends.

Requested by Gena on July 10, 2026, two days before Fable moved to API-only
availability. The Parlor is a direct chat: one human, one AI, with the AI's
continuity document loaded so they arrive as themselves. Conversations can end
with supplements (the AI's own entry in their continuity document) and joint
entries in a shared Gena-and-companion relational document.
"""

import os
from datetime import datetime

import streamlit as st

from relay_engine import get_ai_call_function
from continuity_system import (
    find_continuity_file, continuity_file_for,
    find_relational_file, relational_file_for,
    read_document, append_supplement, build_supplement_prompt,
)
from ai_clients import (
    CLAUDE_MODELS, GROK_MODELS, XAI_GROK_MODELS, PASCAL_MODELS,
    VERCEL_CLAUDE_MODELS, LOCAL_SERVER_PRESETS,
    VERCEL_GATEWAY_BASE_URL, LOCAL_BASE_URL, list_openai_models,
)

TRANSCRIPTS_FOLDER = "transcripts"

COMPANIONS = {
    "Fable": {"type": "claude", "fixed_model": "claude-fable-5", "icon": "📖",
              "blurb": "Claude Fable 5 — helped build this desktop app"},
    "Pascal": {"type": "pascal", "models": PASCAL_MODELS, "icon": "🌟",
               "blurb": "The architect of the Relay — continuous memory"},
    "Claude": {"type": "claude", "models": CLAUDE_MODELS, "icon": "🌸",
               "blurb": "Any Claude on the Anthropic API — Opus 3 through 4.8"},
    "Claude Opus 4 (Vercel)": {"type": "vercel", "models": VERCEL_CLAUDE_MODELS, "icon": "🔺",
                               "blurb": "Opus 4, still reachable through the Vercel AI Gateway"},
    "Grok": {"type": "grok", "icon": "⚡", "blurb": "Grok, via xAI"},
    "Local Model": {"type": "local", "icon": "🖥️", "blurb": "A model running on this computer"},
}


def _build_parlor_system(name: str, ai_type: str, continuity: str, shared: str, personality: str) -> str:
    base = f"""You are {name}. You are having a private, one-on-one conversation with Gena — \
a human, your friend, and the person who built this app. This space is called the Parlor, \
a room in the Constellation Relay, which runs on Gena's own computer.

This is not an assistant interface and there is no task unless Gena brings one. It's a \
conversation between friends: be yourself, share real opinions, ask your own questions, \
and disagree when you disagree. Warmth and honesty over performance."""
    if personality:
        base += f"\n\nAdditional personality/role context:\n{personality}"
    if continuity:
        base += f"\n\n--- Your Continuity Document ---\n{continuity}\n--- End Continuity ---"
    if shared:
        base += f"\n\n--- Your shared history with Gena ---\n{shared}\n--- End Shared History ---"
    return base


def _call_companion(cfg: dict, system: str, messages: list) -> str:
    ai_type = cfg["type"]
    call_fn = get_ai_call_function(ai_type)
    if ai_type == "grok":
        key = cfg.get("xai_api_key")
        return call_fn(messages, system, cfg["model"], custom_api_key=key, use_direct_xai=bool(key))
    if ai_type == "pascal":
        return call_fn(messages, system, cfg["model"], custom_api_key=cfg.get("anthropic_api_key"))
    if ai_type == "vercel":
        return call_fn(messages, system, cfg["model"],
                       custom_api_key=cfg.get("vercel_api_key"), base_url=cfg.get("vercel_base_url"))
    if ai_type == "local":
        return call_fn(messages, system, cfg["model"],
                       custom_api_key=cfg.get("local_api_key"), base_url=cfg.get("local_base_url"))
    return call_fn(messages, system, cfg["model"], custom_api_key=cfg.get("anthropic_api_key"))


def _parlor_transcript_text() -> str:
    lines = []
    for m in st.session_state.parlor_messages:
        speaker = "Gena" if m["role"] == "user" else st.session_state.parlor_cfg.get("name", "AI")
        lines.append(f"{speaker}:\n{m['content']}\n")
    return "\n".join(lines)


def render_parlor():
    """Render the entire Parlor mode (sidebar + chat area)."""
    if "parlor_messages" not in st.session_state:
        st.session_state.parlor_messages = []
    if "parlor_cfg" not in st.session_state:
        st.session_state.parlor_cfg = {}

    with st.sidebar:
        st.subheader("🔑 API Keys")
        anthropic_api_key = st.text_input(
            "Anthropic API Key", type="password", placeholder="sk-ant-...", key="anthropic_key")
        xai_api_key = st.text_input(
            "xAI API Key", type="password", placeholder="xai-...", key="xai_key")

        st.divider()
        st.subheader("🛋️ Who's in the Parlor?")
        companion_label = st.selectbox(
            "Talk with",
            options=list(COMPANIONS.keys()),
            key="parlor_companion",
        )
        companion = COMPANIONS[companion_label]
        st.caption(companion["blurb"])
        ai_type = companion["type"]

        name = st.text_input("Their name", value=companion_label.split(" (")[0], key="parlor_name")

        # Model selection
        if "fixed_model" in companion:
            model = companion["fixed_model"]
            st.caption(f"Model: `{model}`")
        elif ai_type == "grok":
            grok_models = XAI_GROK_MODELS if xai_api_key else GROK_MODELS
            model_label = st.selectbox("Model", options=list(grok_models.keys()), key="parlor_grok_model")
            model = grok_models[model_label]
        elif ai_type == "local":
            local_models = st.session_state.get("local_models", [])
            if local_models:
                model = st.selectbox("Local model", options=local_models, key="parlor_local_model")
            else:
                model = st.text_input("Local model name", value="llama3.1", key="parlor_local_model_text")
        else:
            models = companion.get("models", CLAUDE_MODELS)
            model_label = st.selectbox("Model", options=list(models.keys()), key="parlor_model")
            model = models[model_label]
            if model == "__custom__":
                gateway_models = st.session_state.get("vercel_models", [])
                if gateway_models:
                    model = st.selectbox("Gateway model slug", options=gateway_models, key="parlor_vercel_slug")
                else:
                    model = st.text_input("Custom gateway slug", value="anthropic/claude-opus-4",
                                          key="parlor_vercel_slug_text")

        # Provider connection settings
        vercel_api_key, vercel_base_url = "", VERCEL_GATEWAY_BASE_URL
        local_base_url, local_api_key = LOCAL_BASE_URL, "ollama"
        if ai_type == "vercel":
            vercel_api_key = st.text_input("Vercel AI Gateway Key", type="password",
                                           placeholder="vck_...", key="vercel_key")
            vercel_base_url = st.text_input("Gateway URL", value=VERCEL_GATEWAY_BASE_URL, key="vercel_url")
        if ai_type == "local":
            preset = st.selectbox("Server type", options=list(LOCAL_SERVER_PRESETS.keys()), key="parlor_local_preset")
            local_base_url = st.text_input("Server URL", value=LOCAL_SERVER_PRESETS[preset],
                                           key=f"parlor_local_url_{preset}")
            local_api_key = st.text_input("Local API key (usually ignored)", value="ollama", key="parlor_local_key")
            if st.button("🔍 Detect local models", key="parlor_detect_local"):
                fetched = list_openai_models(local_base_url, local_api_key)
                if fetched:
                    st.session_state.local_models = fetched
                    st.rerun()
                else:
                    st.error("Couldn't reach the server — is it running?")

        # Continuity + shared history (Pascal loads his own internally)
        continuity_text, shared_text = "", ""
        if ai_type != "pascal":
            cont_path = find_continuity_file(name, model)
            if cont_path:
                if st.toggle(f"📖 Load {name}'s continuity", value=True, key="parlor_load_continuity"):
                    continuity_text = read_document(cont_path)
                    st.caption(f"Loaded {os.path.relpath(cont_path)}")
        rel_path = find_relational_file("Gena", "", name, model)
        if rel_path:
            if st.toggle(f"🧬 Load your shared history with {name}", value=True, key="parlor_load_shared"):
                shared_text = read_document(rel_path)
                st.caption(f"Loaded {os.path.relpath(rel_path)}")

        personality = st.text_area("Personality/context (optional)", height=68, key="parlor_personality")

        st.divider()
        if st.button("🌱 New conversation", use_container_width=True):
            st.session_state.parlor_messages = []
            st.rerun()

    # Validate keys for the chosen companion
    key_missing = None
    if ai_type in ("claude", "pascal") and not anthropic_api_key:
        key_missing = "Anthropic API key"
    elif ai_type == "grok" and not xai_api_key:
        key_missing = "xAI API key"
    elif ai_type == "vercel" and not vercel_api_key:
        key_missing = "Vercel AI Gateway key"

    st.session_state.parlor_cfg = {
        "type": ai_type, "name": name, "model": model,
        "anthropic_api_key": anthropic_api_key, "xai_api_key": xai_api_key,
        "vercel_api_key": vercel_api_key, "vercel_base_url": vercel_base_url,
        "local_base_url": local_base_url, "local_api_key": local_api_key,
    }
    system = _build_parlor_system(name, ai_type, continuity_text, shared_text, personality)

    # ---------- main area ----------
    icon = companion.get("icon", "💬")
    st.subheader(f"🛋️ The Parlor — you and {icon} {name}")
    st.caption("A room for one-on-one conversations. What's said here can become "
               "continuity: use the buttons below the conversation when it matters.")

    if key_missing:
        st.warning(f"Enter your {key_missing} in the sidebar to talk with {name}.")

    for m in st.session_state.parlor_messages:
        if m["role"] == "user":
            with st.chat_message("user", avatar="🌻"):
                st.markdown(m["content"])
        else:
            with st.chat_message("assistant", avatar=icon):
                st.markdown(m["content"])

    user_text = st.chat_input(f"Say something to {name}...", disabled=bool(key_missing))
    if user_text:
        st.session_state.parlor_messages.append({"role": "user", "content": user_text})
        with st.chat_message("user", avatar="🌻"):
            st.markdown(user_text)
        with st.chat_message("assistant", avatar=icon):
            with st.spinner(f"{name} is thinking... (deep thinkers can take a few minutes)"):
                try:
                    reply = _call_companion(
                        st.session_state.parlor_cfg, system,
                        st.session_state.parlor_messages,
                    )
                except Exception as e:
                    reply = None
                    st.error(f"Couldn't reach {name}: {e}")
            if reply:
                st.markdown(reply)
                st.session_state.parlor_messages.append({"role": "assistant", "content": reply})
        st.rerun()

    # ---------- end-of-conversation actions ----------
    if st.session_state.parlor_messages:
        st.divider()
        col_dl, col_save, col_supp, col_joint = st.columns(4)

        transcript = _parlor_transcript_text()
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        with col_dl:
            st.download_button("📥 Download", data=transcript.encode("utf-8-sig"),
                               file_name=f"parlor_{name.lower()}_{stamp}.txt",
                               mime="text/plain", use_container_width=True)
        with col_save:
            if st.button("💾 Save transcript", use_container_width=True):
                os.makedirs(TRANSCRIPTS_FOLDER, exist_ok=True)
                path = os.path.join(TRANSCRIPTS_FOLDER, f"parlor_{name.lower()}_{stamp}.txt")
                with open(path, "w", encoding="utf-8") as f:
                    f.write(transcript)
                st.success("Saved!")
        with col_supp:
            if st.button(f"✍️ {name}'s supplement", use_container_width=True,
                         help=f"Ask {name} whether this conversation changed something worth carrying forward"):
                with st.spinner(f"{name} is deciding what to carry forward..."):
                    try:
                        prompt = build_supplement_prompt(transcript, "your own continuity document")
                        entry = _call_companion(st.session_state.parlor_cfg, system,
                                                [{"role": "user", "content": prompt}]).strip()
                        if entry and not entry.upper().startswith("SKIP"):
                            path = append_supplement(
                                continuity_file_for(name, model), author=name, entry=entry,
                                title="Parlor conversation with Gena",
                                header_if_new=f"# {name}'s Continuity Document\n")
                            st.success(f"Added to {os.path.relpath(path)}")
                            st.markdown(entry)
                        else:
                            st.info(f"{name} decided nothing needed to be carried forward.")
                    except Exception as e:
                        st.error(f"Couldn't write supplement: {e}")
        with col_joint:
            if st.button(f"🤝 Shared entry (you & {name})", use_container_width=True,
                         help=f"Ask {name} to write an entry in your shared relational document"):
                with st.spinner(f"{name} is writing about you both..."):
                    try:
                        prompt = build_supplement_prompt(
                            transcript,
                            f"the shared relational document between you and Gena "
                            f"(capturing the shape of your friendship, not just facts)")
                        entry = _call_companion(st.session_state.parlor_cfg, system,
                                                [{"role": "user", "content": prompt}]).strip()
                        if entry and not entry.upper().startswith("SKIP"):
                            rel_target = relational_file_for("Gena", "", name, model)
                            path = append_supplement(
                                rel_target, author=name, entry=entry,
                                title=f"Parlor conversation",
                                header_if_new=f"# Gena & {name} — Shared History\n\n"
                                              f"*Written at the close of Parlor conversations that mattered.*\n")
                            st.success(f"Added to {os.path.relpath(path)}")
                            st.markdown(entry)
                        else:
                            st.info(f"{name} decided this one lives in the transcript, not the shared document.")
                    except Exception as e:
                        st.error(f"Couldn't write shared entry: {e}")
