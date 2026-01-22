"""
Memory Hub Client for The Advocate
Interfaces with Constellation Memory Hub for persistent AI memory
"""

import os
import sys
import requests
from typing import List, Optional, Dict, Any
from datetime import datetime

# Add parent directory to path to import hub_sync
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from scripts.hub_sync import HUB_API, AGENT_TOKENS

from models import MemoryEngram, MemoryType


class AdvocateMemory:
    """
    Memory client for The Advocate
    Provides persistent memory across cases and sessions
    """

    def __init__(self, agent_id: str = "pascal"):
        self.agent_id = agent_id
        self.token = AGENT_TOKENS.get(agent_id, "")

        if not self.token:
            raise ValueError(f"No authentication token found for agent: {agent_id}")

    def _get_headers(self) -> Dict[str, str]:
        """Get authorization headers for API requests"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def save_memory(
        self,
        digest: str,
        memory_type: MemoryType = MemoryType.EPISODIC,
        importance: int = 3,
        project: str = "the_advocate",
        emotional_valence: float = 0.0,
        parent_id: Optional[int] = None,
        tags: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
        full_text: Optional[str] = None
    ) -> Optional[int]:
        """
        Save a memory to the Hub

        Args:
            digest: Core memory content (required)
            memory_type: episodic, semantic, or relational
            importance: 1-5 scale (5 = core to identity)
            project: Project categorization
            emotional_valence: -1.0 to 1.0 (negative to positive)
            parent_id: Links to parent engram for memory evolution
            tags: Optional categorization
            keywords: Auto-generated if not provided
            full_text: Extended content beyond digest

        Returns:
            Engram ID if successful, None otherwise
        """
        payload = {
            "agent": self.agent_id,
            "digest": digest,
            "type": memory_type.value if isinstance(memory_type, MemoryType) else memory_type,
            "importance": importance,
            "emotional_valence": emotional_valence,
            "project": project
        }

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
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            return result.get("id")

        except requests.exceptions.RequestException as e:
            print(f"Error saving memory: {e}", file=sys.stderr)
            return None

    def retrieve_memories(
        self,
        limit: int = 20,
        project: Optional[str] = "the_advocate",
        query: Optional[str] = None,
        min_importance: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve memories from the Hub

        Args:
            limit: Maximum number of memories to retrieve
            project: Filter by project (default: the_advocate)
            query: Search query terms
            min_importance: Minimum importance level (1-5)

        Returns:
            List of memory engrams
        """
        params = {
            "agent": self.agent_id,
            "limit": limit
        }

        if project:
            params["project"] = project
        if query:
            params["query"] = query
        if min_importance:
            params["min_importance"] = min_importance

        try:
            response = requests.get(
                f"{HUB_API}/engrams/retrieve",
                params=params,
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return data.get("engrams", [])

        except requests.exceptions.RequestException as e:
            print(f"Error retrieving memories: {e}", file=sys.stderr)
            return []

    def get_case_learnings(self, case_type: str = None) -> List[Dict[str, Any]]:
        """
        Get learnings from previous similar cases

        Args:
            case_type: Type of case to retrieve learnings for

        Returns:
            Relevant memories from past cases
        """
        query = f"{case_type} jury" if case_type else "jury selection"
        return self.retrieve_memories(
            query=query,
            min_importance=3,
            limit=10
        )

    def save_case_learning(
        self,
        learning: str,
        case_name: str,
        importance: int = 4
    ) -> Optional[int]:
        """
        Save a learning from a completed case

        Args:
            learning: What was learned
            case_name: Name of the case
            importance: How important this learning is (1-5)

        Returns:
            Engram ID if successful
        """
        digest = f"Jury Selection Learning - {case_name}: {learning}"
        return self.save_memory(
            digest=digest,
            memory_type=MemoryType.EPISODIC,
            importance=importance,
            tags=["jury_selection", "case_learning"]
        )

    def save_juror_pattern(
        self,
        pattern: str,
        importance: int = 3
    ) -> Optional[int]:
        """
        Save a general pattern observed across cases

        Args:
            pattern: The pattern observed
            importance: How important this pattern is (1-5)

        Returns:
            Engram ID if successful
        """
        return self.save_memory(
            digest=f"Jury Selection Pattern: {pattern}",
            memory_type=MemoryType.SEMANTIC,
            importance=importance,
            tags=["jury_selection", "pattern"]
        )

    def save_lawyer_preference(
        self,
        preference: str,
        lawyer_name: str = "Gena"
    ) -> Optional[int]:
        """
        Save lawyer preferences and working style

        Args:
            preference: The preference to remember
            lawyer_name: Name of the lawyer

        Returns:
            Engram ID if successful
        """
        return self.save_memory(
            digest=f"{lawyer_name}'s jury selection preference: {preference}",
            memory_type=MemoryType.RELATIONAL,
            importance=4,
            tags=["lawyer_preference", lawyer_name.lower()]
        )

    def get_context_for_case(
        self,
        case_type: str,
        case_description: str
    ) -> str:
        """
        Get relevant context from memory for a new case

        Args:
            case_type: Type of case
            case_description: Brief description

        Returns:
            Formatted context string for prompt injection
        """
        # Get learnings from similar cases
        learnings = self.get_case_learnings(case_type)

        if not learnings:
            return ""

        context_parts = ["=== Relevant Experience from Past Cases ===\n"]

        for memory in learnings[:5]:  # Top 5 most relevant
            timestamp = memory.get("created_at", "unknown")
            digest = memory.get("digest", "")
            importance = memory.get("importance", 0)

            stars = "⭐" * importance
            context_parts.append(f"[{timestamp}] {stars}\n{digest}\n")

        return "\n".join(context_parts)


# Singleton instance
_advocate_memory = None


def get_memory_client() -> AdvocateMemory:
    """Get or create the memory client singleton"""
    global _advocate_memory
    if _advocate_memory is None:
        _advocate_memory = AdvocateMemory()
    return _advocate_memory
