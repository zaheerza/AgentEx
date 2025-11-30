"""
Configuration settings for the multi-agent system.
"""

import os
from typing import Optional
from pathlib import Path

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file from current directory
except ImportError:
    # python-dotenv not installed, will use system environment variables only
    pass


class Settings:
    """Application settings loaded from environment variables or .env file"""

    def __init__(self):
        """Initialize settings from environment variables"""

        # =================================================================
        # API Keys - LLM Providers
        # =================================================================
        # Anthropic (Claude) - Currently required
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

        # Groq - Optional (for future multi-provider support)
        self.groq_api_key = os.getenv("GROQ_API_KEY")

        # OpenAI (GPT) - Optional
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

        # HuggingFace - Optional
        self.huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")

        # =================================================================
        # Model Configuration
        # =================================================================
        # Anthropic model (currently active)
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")

        # Optional: Other provider models
        self.groq_model = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4")
        self.huggingface_model = os.getenv("HUGGINGFACE_MODEL", "meta-llama/Llama-2-70b-chat-hf")

        # =================================================================
        # System Configuration
        # =================================================================
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
            print("\n" + "="*60)
            print("❌ Error: ANTHROPIC_API_KEY not configured")
            print("="*60)
            print("\nThe system requires an Anthropic API key to function.")
            print("\nOption 1: Create a .env file (Recommended)")
            print("  1. Copy the example: cp .env.example .env")
            print("  2. Edit .env and add your key:")
            print("     ANTHROPIC_API_KEY=sk-ant-your-key-here")
            print("  3. Get a key from: https://console.anthropic.com/")
            print("\nOption 2: Set environment variable")
            print("  export ANTHROPIC_API_KEY='your-api-key'")
            print("\nSee ENV_SETUP.md for detailed instructions.")
            print("="*60 + "\n")
            return False

        return True

    def get_available_providers(self) -> list[str]:
        """
        Get list of configured LLM providers.

        Returns:
            List of provider names that have API keys configured
        """
        providers = []

        if self.anthropic_api_key:
            providers.append("anthropic")
        if self.groq_api_key:
            providers.append("groq")
        if self.openai_api_key:
            providers.append("openai")
        if self.huggingface_api_key:
            providers.append("huggingface")

        return providers

    def __repr__(self) -> str:
        """String representation (hides API keys)"""
        providers = self.get_available_providers()

        return f"""Settings(
    model={self.model},
    db_path={self.db_path},
    max_iterations={self.max_agent_iterations},
    verbose={self.verbose},
    configured_providers={providers}
)"""
