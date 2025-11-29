"""
Configuration settings for the multi-agent system.
"""

import os
from typing import Optional
from pathlib import Path


class Settings:
    """Application settings"""

    def __init__(self):
        """Initialize settings from environment variables"""

        # API Keys
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

        # Model configuration
        self.model = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5-20250929")

        # Database
        self.db_path = os.getenv("DB_PATH", "data/memory.db")

        # Agent configuration
        self.max_agent_iterations = int(os.getenv("MAX_AGENT_ITERATIONS", "15"))

        # Logging
        self.verbose = os.getenv("VERBOSE", "true").lower() == "true"

    def validate(self) -> bool:
        """
        Validate that required settings are present.

        Returns:
            True if valid, False otherwise
        """
        if not self.anthropic_api_key:
            print("❌ Error: ANTHROPIC_API_KEY environment variable not set")
            print("Please set it with: export ANTHROPIC_API_KEY='your-api-key'")
            return False

        return True

    def __repr__(self) -> str:
        """String representation (hides API key)"""
        return f"""Settings(
    model={self.model},
    db_path={self.db_path},
    max_iterations={self.max_agent_iterations},
    api_key={'***' if self.anthropic_api_key else 'NOT SET'}
)"""
