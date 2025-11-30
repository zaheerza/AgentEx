"""
Core data types used across the multi-agent system.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid


@dataclass
class AgentCapability:
    """
    Describes what an agent can do.
    Used by orchestrator for intent matching and routing.
    """
    name: str
    description: str
    keywords: List[str]  # Keywords for intent matching
    required_inputs: List[str]  # Required parameters
    optional_inputs: List[str] = field(default_factory=list)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    examples: List[str] = field(default_factory=list)  # Example queries

    def matches_intent(self, query: str) -> float:
        """
        Calculate match score (0-1) between query and this capability.

        Args:
            query: User query string

        Returns:
            Match score from 0.0 (no match) to 1.0 (perfect match)
        """
        query_lower = query.lower()
        score = 0.0

        # Check keyword matches
        keyword_matches = sum(1 for kw in self.keywords if kw.lower() in query_lower)
        if keyword_matches > 0:
            score = min(1.0, keyword_matches * 0.3)

        # Check if capability name is mentioned
        if self.name.lower() in query_lower:
            score = max(score, 0.5)

        return score


@dataclass
class Intent:
    """
    Represents the parsed intent from a user query.
    """
    primary_action: str  # e.g., "find_restaurants", "track_feedback"
    entities: Dict[str, Any]  # Extracted entities (location, cuisine, etc.)
    confidence: float  # Confidence score 0-1
    matched_capability: Optional[AgentCapability] = None
    raw_query: str = ""


@dataclass
class Task:
    """
    A task to be executed by an agent.
    """
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)  # Shared context
    priority: int = 1
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Ensure created_at is a datetime object"""
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)


@dataclass
class AgentResult:
    """
    Result from agent execution.
    """
    task_id: str
    agent_name: str
    success: bool
    data: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "task_id": self.task_id,
            "agent_name": self.agent_name,
            "success": self.success,
            "data": self.data,
            "metadata": self.metadata,
            "error": self.error,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class ToolDefinition:
    """
    Definition of a tool that an agent can use.
    """
    name: str
    description: str
    input_schema: Dict[str, Any]

    def to_anthropic_format(self) -> Dict[str, Any]:
        """Convert to Anthropic API tool format"""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema
        }


@dataclass
class ConversationMessage:
    """
    A message in the conversation history.
    """
    role: str  # 'user' or 'assistant'
    content: Any  # Can be string or list of content blocks
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
