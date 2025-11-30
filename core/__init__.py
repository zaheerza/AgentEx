"""
Core framework for the multi-agent system.
"""

from .types import Task, AgentResult, AgentCapability, Intent
from .base_agent import BaseAgent
from .orchestrator import OrchestratorAgent

__all__ = [
    'Task',
    'AgentResult',
    'AgentCapability',
    'Intent',
    'BaseAgent',
    'OrchestratorAgent',
]
