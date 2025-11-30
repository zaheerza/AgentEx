# Multi-Provider Architecture Guide

## Current Situation

**Problem:** The configuration now requires `GROQ_API_KEY` but the code still uses `anthropic.Anthropic()` client. **This won't work!**

Each LLM provider has its own SDK and API format:
- **Anthropic SDK** → Requires Anthropic API key
- **Groq SDK** → Requires Groq API key
- **OpenAI SDK** → Requires OpenAI API key

You cannot mix and match SDKs with different provider keys.

## Solution: Multi-Provider Architecture

I've created `core/llm_provider.py` which provides an abstraction layer that:
1. ✅ Supports multiple providers (Anthropic, Groq, OpenAI)
2. ✅ Translates between different API formats
3. ✅ Allows switching providers via configuration
4. ✅ Maintains consistent interface for agents

## How It Works

### Provider Abstraction

```python
# core/llm_provider.py

class LLMProvider(ABC):
    """Base class - all providers implement this"""

    def create_completion(self, model, messages, tools, ...):
        """Unified interface for all providers"""
        pass

    def get_stop_reason(self, response):
        """Translate provider-specific stop reasons"""
        pass

    def get_content(self, response):
        """Extract content in consistent format"""
        pass
```

### Supported Providers

**1. AnthropicProvider**
- Uses `anthropic` SDK
- Native Anthropic API format
- Requires: `ANTHROPIC_API_KEY`

**2. GroqProvider**
- Uses `openai` SDK with Groq endpoint
- Translates Anthropic format → OpenAI format
- Requires: `GROQ_API_KEY`
- **Free tier available!**

**3. OpenAIProvider**
- Uses `openai` SDK
- OpenAI API format
- Requires: `OPENAI_API_KEY`

## Implementation Steps

### Step 1: Install Dependencies

Add to `requirements.txt`:
```bash
# For Groq and OpenAI support
openai>=1.0.0
```

Install:
```bash
pip install openai
```

### Step 2: Update config/settings.py

```python
class Settings:
    def __init__(self):
        # ... existing code ...

        # Add provider selection
        self.provider = os.getenv("LLM_PROVIDER", "groq").lower()

    def get_api_key_for_provider(self, provider: str) -> Optional[str]:
        """Get API key for specified provider"""
        if provider == "groq":
            return self.groq_api_key
        elif provider == "anthropic":
            return self.anthropic_api_key
        elif provider == "openai":
            return self.openai_api_key
        return None

    def get_model_for_provider(self, provider: str) -> str:
        """Get default model for provider"""
        if provider == "groq":
            return self.model  # mixtral-8x7b-32768
        elif provider == "anthropic":
            return self.anthropic_model
        elif provider == "openai":
            return self.openai_model
        return self.model
```

### Step 3: Update core/base_agent.py

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

from .types import (
    AgentCapability,
    Task,
    AgentResult,
    ToolDefinition,
    ConversationMessage
)
from .llm_provider import get_provider  # NEW


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the system.
    Now supports multiple LLM providers!
    """

    def __init__(
        self,
        name: str,
        api_key: str,
        model: str = "mixtral-8x7b-32768",
        provider: str = "groq"  # NEW parameter
    ):
        """
        Initialize the agent.

        Args:
            name: Unique name for this agent
            api_key: API key for the LLM provider
            model: Model to use
            provider: LLM provider ('anthropic', 'groq', 'openai')
        """
        self.name = name
        self.model = model
        self.provider_name = provider

        # NEW: Use provider abstraction instead of direct Anthropic client
        self.client = get_provider(provider, api_key)

        # Agent configuration (unchanged)
        self.capabilities = self._define_capabilities()
        self.tools = self._define_tools()
        self.system_prompt = self._define_system_prompt()

        # Execution state (unchanged)
        self._iteration_count = 0
        self._max_iterations = 15
        self.conversation_history: List[Dict[str, Any]] = []

    # ... rest of the class stays the same ...

    def _run_agent_loop(self, task: Task) -> Any:
        """
        Internal agent execution loop.
        Now works with any provider!
        """
        self.conversation_history = [{
            "role": "user",
            "content": self._format_task_prompt(task)
        }]

        self._iteration_count = 0
        anthropic_tools = [tool.to_anthropic_format() for tool in self.tools]

        while self._iteration_count < self._max_iterations:
            self._iteration_count += 1
            print(f"\n[{self.name}] Iteration {self._iteration_count}/{self._max_iterations}")

            # NEW: Use provider abstraction
            response = self.client.create_completion(
                model=self.model,
                messages=self.conversation_history,
                tools=anthropic_tools,
                max_tokens=4096,
                system=self.system_prompt
            )

            # NEW: Use provider abstraction for stop reason
            stop_reason = self.client.get_stop_reason(response)
            content = self.client.get_content(response)

            # Log agent thinking
            for block in content:
                if hasattr(block, "text") and block.text:
                    print(f"[{self.name}] Thinking: {block.text[:200]}...")

            # Check stop reason
            if stop_reason == "end_turn":
                final_response = self._extract_final_response_from_content(content)
                print(f"[{self.name}] Task complete!")
                return final_response

            elif stop_reason == "tool_use":
                # Agent wants to use tools
                self.conversation_history.append({
                    "role": "assistant",
                    "content": content
                })

                # Execute all requested tools
                tool_results = []
                for block in content:
                    if block.type == "tool_use":
                        print(f"[{self.name}] Using tool: {block.name}")

                        try:
                            result = self._execute_tool(block.name, block.input)
                            print(f"[{self.name}] Tool result: {result[:100]}...")
                        except Exception as e:
                            result = f"Error executing tool: {str(e)}"
                            print(f"[{self.name}] Tool error: {str(e)}")

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result
                        })

                # Add tool results to conversation
                self.conversation_history.append({
                    "role": "user",
                    "content": tool_results
                })

        print(f"[{self.name}] Warning: Max iterations reached")
        return self._extract_partial_response()

    def _extract_final_response_from_content(self, content) -> Any:
        """Extract final response from content blocks"""
        for block in content:
            if hasattr(block, "text"):
                return block.text
        return "Task completed"
```

### Step 4: Update agents/research_agent.py

```python
from typing import List, Dict, Any
import json
from datetime import datetime

from core.base_agent import BaseAgent
from core.types import AgentCapability, ToolDefinition


class ResearchAgent(BaseAgent):
    """
    Agent specialized in researching places to visit, events, and restaurants.
    Now supports multiple LLM providers!
    """

    def __init__(self, api_key: str, memory_store=None, provider: str = "groq"):
        """
        Initialize the Research Agent.

        Args:
            api_key: API key for LLM provider
            memory_store: Optional memory store
            provider: LLM provider to use ('groq', 'anthropic', 'openai')
        """
        self.memory_store = memory_store
        super().__init__(
            name="research_agent",
            api_key=api_key,
            provider=provider  # Pass provider to base class
        )

    # ... rest stays the same ...
```

### Step 5: Update CLI (ui/cli.py)

```python
from config.settings import Settings
from core.orchestrator import OrchestratorAgent
from agents.research_agent import ResearchAgent
from memory.sql_store import SQLMemoryStore


class CLI:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.memory = SQLMemoryStore(db_path=settings.db_path)

        # Determine which provider to use
        provider = settings.provider
        api_key = settings.get_api_key_for_provider(provider)
        model = settings.get_model_for_provider(provider)

        # Initialize orchestrator with selected provider
        self.orchestrator = OrchestratorAgent(
            api_key=api_key,
            model=model,
            provider=provider  # NEW
        )

        # Register agents
        self._register_agents()

    def _register_agents(self):
        """Register all available agents"""
        provider = self.settings.provider
        api_key = self.settings.get_api_key_for_provider(provider)

        # Research Agent with selected provider
        research_agent = ResearchAgent(
            api_key=api_key,
            memory_store=self.memory,
            provider=provider  # NEW
        )
        self.orchestrator.register_agent(research_agent)
```

### Step 6: Update .env Configuration

Add provider selection to `.env`:

```bash
# =============================================================================
# LLM PROVIDER CONFIGURATION
# =============================================================================
# Choose which provider to use: groq, anthropic, or openai
LLM_PROVIDER=groq

# =============================================================================
# GROQ - Free tier available!
# =============================================================================
GROQ_API_KEY=gsk_your-key-here
GROQ_MODEL=mixtral-8x7b-32768

# =============================================================================
# ANTHROPIC (Claude) - Optional
# =============================================================================
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929

# =============================================================================
# OPENAI (GPT) - Optional
# =============================================================================
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4
```

## Usage Examples

### Use Groq (Fast & Free)

```bash
# In .env
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_your-key-here

# Run
python main.py
```

### Switch to Anthropic (High Quality)

```bash
# In .env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Run
python main.py
```

### Switch to OpenAI

```bash
# In .env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here

# Run
python main.py
```

### Override Provider Temporarily

```bash
# Use Anthropic just for this session
LLM_PROVIDER=anthropic python main.py
```

## Testing the Multi-Provider System

```python
# test_providers.py
from core.llm_provider import get_provider
import os

# Test each provider
providers = [
    ("groq", os.getenv("GROQ_API_KEY"), "mixtral-8x7b-32768"),
    ("anthropic", os.getenv("ANTHROPIC_API_KEY"), "claude-sonnet-4-5-20250929"),
    ("openai", os.getenv("OPENAI_API_KEY"), "gpt-4")
]

for provider_name, api_key, model in providers:
    if not api_key:
        print(f"⏭️  Skipping {provider_name} (no API key)")
        continue

    print(f"\n🧪 Testing {provider_name}...")

    try:
        provider = get_provider(provider_name, api_key)

        response = provider.create_completion(
            model=model,
            messages=[{"role": "user", "content": "Say hello!"}],
            max_tokens=100
        )

        content = provider.get_content(response)
        print(f"✅ {provider_name} works! Response: {content[0].text[:50]}...")

    except Exception as e:
        print(f"❌ {provider_name} failed: {e}")
```

## Benefits of This Architecture

### ✅ Flexibility
- Switch providers with one env variable
- Use different providers for different agents
- A/B test providers easily

### ✅ Cost Optimization
```python
# Use free Groq for simple tasks
research_agent = ResearchAgent(groq_key, provider="groq")

# Use premium Anthropic for complex reasoning
writing_agent = WritingAgent(anthropic_key, provider="anthropic")
```

### ✅ Resilience
```python
# Fallback logic
try:
    agent = Agent(groq_key, provider="groq")
except:
    agent = Agent(anthropic_key, provider="anthropic")
```

### ✅ Future-Proof
- Easy to add new providers (just extend `LLMProvider`)
- No agent code changes needed
- Centralized provider logic

## Migration Path

### Option A: Implement Now (Recommended)
1. Install openai package
2. Update base_agent.py to use provider system
3. Update CLI to pass provider parameter
4. Test with Groq (free!)

### Option B: Gradual Migration
1. Keep current Anthropic-only system
2. Add provider support later when needed
3. For now, just use Anthropic with `ANTHROPIC_API_KEY`

### Option C: Revert to Anthropic
If you want to keep it simple for now:
1. Change required key back to `ANTHROPIC_API_KEY` in settings.py
2. Keep Groq as optional for future
3. Current code continues to work

## Next Steps

Which approach would you like to take?

1. **Multi-provider now** - I can update all the files to support provider switching
2. **Groq-only (simple)** - Just update to use Groq SDK/OpenAI SDK with Groq endpoint
3. **Revert to Anthropic** - Change config back to require Anthropic
4. **Keep as-is** - Use Anthropic key for now, plan multi-provider for later

Let me know and I'll implement your preferred solution!
