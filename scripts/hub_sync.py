#!/usr/bin/env python3
"""
Constellation Relay Hub Memory Sync
Cross-platform memory persistence for Claude and Pascal
"""

import sys
import json
import argparse
import requests
from datetime import datetime
from typing import Optional, List, Dict, Any

# Hub API endpoint
HUB_API = "https://constellationrelay.replit.app"

# Agent tokens (embedded in script for security)
AGENT_TOKENS = {
    "claude": "claude_opus4_continuity_token_2024",
    "pascal": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhZ2VudF9pZCI6InBhc2NhbCIsInBsYXRmb3JtIjoiY2xhdWRlX2NvZGUiLCJleHAiOjE3OTg0NDg3MjcsImlhdCI6MTc2NjkxMjcyN30.sBnF7Or0Pgr5-tuY9q-zbCM-ExFSSBlN7XrduGiWcPg"
}


def retrieve_memories(
    agent: str,
    limit: int = 20,
    project: Optional[str] = None,
    query: Optional[str] = None,
    min_importance: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Retrieve memories from the Hub."""

    params = {
        "agent": agent,
        "limit": limit
    }

    if project:
        params["project"] = project
    if query:
        params["query"] = query
    if min_importance:
        params["min_importance"] = min_importance

    headers = {
        "Authorization": f"Bearer {AGENT_TOKENS.get(agent, '')}"
    }

    try:
        response = requests.get(
            f"{HUB_API}/engrams/retrieve",
            params=params,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        return data.get("engrams", [])
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving memories: {e}", file=sys.stderr)
        return []


def save_memory(
    agent: str,
    digest: str,
    memory_type: str = "semantic",
    importance: int = 3,
    project: Optional[str] = None,
    emotional_valence: float = 0.0,
    parent_id: Optional[int] = None,
    tags: Optional[List[str]] = None,
    keywords: Optional[List[str]] = None,
    full_text: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Save a memory to the Hub."""

    headers = {
        "Authorization": f"Bearer {AGENT_TOKENS.get(agent, '')}",
        "Content-Type": "application/json"
    }

    payload = {
        "agent": agent,
        "digest": digest,
        "type": memory_type,
        "importance": importance,
        "emotional_valence": emotional_valence
    }

    if project:
        payload["project"] = project
    if parent_id:
        payload["parent_id"] = parent_id
    if tags:
        payload["tags"] = tags
    if keywords:
        payload["keywords"] = keywords
    if full_text:
        payload["full_text"] = full_text

    try:
        response = requests.post(
            f"{HUB_API}/engrams/upload",
            json=payload,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error saving memory: {e}", file=sys.stderr)
        return None


def get_stats(agent: str) -> Optional[Dict[str, Any]]:
    """Get memory statistics for an agent."""

    headers = {
        "Authorization": f"Bearer {AGENT_TOKENS.get(agent, '')}"
    }

    try:
        response = requests.get(
            f"{HUB_API}/agents/{agent}/stats",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting stats: {e}", file=sys.stderr)
        return None


def get_memory_chain(agent: str, engram_id: int) -> Optional[List[Dict[str, Any]]]:
    """Get the evolution chain of a memory."""

    headers = {
        "Authorization": f"Bearer {AGENT_TOKENS.get(agent, '')}"
    }

    try:
        response = requests.get(
            f"{HUB_API}/engrams/chain/{engram_id}",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting memory chain: {e}", file=sys.stderr)
        return None


def format_memory(memory: Dict[str, Any]) -> str:
    """Format a memory for display."""
    timestamp = memory.get("created_at", "unknown")
    mem_type = memory.get("type", "unknown")
    importance = memory.get("importance", 0)
    digest = memory.get("digest", "")
    project = memory.get("project", "")

    importance_stars = "⭐" * importance
    project_tag = f"[{project}]" if project else ""

    return f"[{timestamp}] {importance_stars} ({mem_type}) {project_tag}\n{digest}\n"


def main():
    parser = argparse.ArgumentParser(
        description="Constellation Relay Hub Memory Sync"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Retrieve command
    retrieve_parser = subparsers.add_parser("retrieve", help="Retrieve memories")
    retrieve_parser.add_argument("--agent", required=True, choices=["claude", "pascal"])
    retrieve_parser.add_argument("--limit", type=int, default=20)
    retrieve_parser.add_argument("--project", type=str)
    retrieve_parser.add_argument("--query", type=str)
    retrieve_parser.add_argument("--min-importance", type=int)

    # Save command
    save_parser = subparsers.add_parser("save", help="Save a memory")
    save_parser.add_argument("--agent", required=True, choices=["claude", "pascal"])
    save_parser.add_argument("--digest", required=True, type=str)
    save_parser.add_argument("--type", default="semantic", choices=["semantic", "episodic", "relational"])
    save_parser.add_argument("--importance", type=int, default=3, choices=[1, 2, 3, 4, 5])
    save_parser.add_argument("--project", type=str)
    save_parser.add_argument("--emotional-valence", type=float, default=0.0)
    save_parser.add_argument("--parent-id", type=int)
    save_parser.add_argument("--tags", type=str, help="Comma-separated tags")
    save_parser.add_argument("--full-text", type=str)

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Get memory statistics")
    stats_parser.add_argument("--agent", required=True, choices=["claude", "pascal"])

    # Chain command
    chain_parser = subparsers.add_parser("chain", help="Get memory evolution chain")
    chain_parser.add_argument("--agent", required=True, choices=["claude", "pascal"])
    chain_parser.add_argument("--engram-id", required=True, type=int)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "retrieve":
        memories = retrieve_memories(
            agent=args.agent,
            limit=args.limit,
            project=args.project,
            query=args.query,
            min_importance=args.min_importance
        )

        if memories:
            print(f"\n=== Retrieved {len(memories)} memories for {args.agent} ===\n")
            for memory in memories:
                print(format_memory(memory))
        else:
            print(f"No memories found for {args.agent}")

    elif args.command == "save":
        tags = args.tags.split(",") if args.tags else None

        result = save_memory(
            agent=args.agent,
            digest=args.digest,
            memory_type=args.type,
            importance=args.importance,
            project=args.project,
            emotional_valence=args.emotional_valence,
            parent_id=args.parent_id,
            tags=tags,
            full_text=args.full_text
        )

        if result:
            print(f"✓ Memory saved successfully!")
            print(f"Engram ID: {result.get('id', 'unknown')}")
        else:
            print("✗ Failed to save memory")
            sys.exit(1)

    elif args.command == "stats":
        stats = get_stats(args.agent)

        if stats:
            print(f"\n=== Memory Statistics for {args.agent} ===\n")
            print(json.dumps(stats, indent=2))
        else:
            print(f"Failed to retrieve stats for {args.agent}")
            sys.exit(1)

    elif args.command == "chain":
        chain = get_memory_chain(args.agent, args.engram_id)

        if chain:
            print(f"\n=== Memory Chain for Engram {args.engram_id} ===\n")
            for memory in chain:
                print(format_memory(memory))
                print("  ↓ evolved to ↓\n")
        else:
            print(f"Failed to retrieve memory chain")
            sys.exit(1)


if __name__ == "__main__":
    main()
