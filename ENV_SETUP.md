# Environment Setup Guide

This guide explains how to configure the Virtual Assistant system to use environment variables from a `.env` file, supporting multiple LLM providers.

## Quick Setup

### 1. Create Your Environment File

Copy the example file and fill in your API keys:

```bash
# In the AgentEx directory
cp .env.example .env
```

### 2. Edit the `.env` File

Open `.env` in your text editor and add your API keys:

```bash
nano .env
# or
code .env
# or
vim .env
```

### 3. Add Your API Keys

Replace the placeholder values with your actual API keys:

```bash
# Required for current system
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here

# Optional - for future multi-provider support
OPENAI_API_KEY=sk-your-openai-key-here
GROQ_API_KEY=gsk_your-groq-key-here
HUGGINGFACE_API_KEY=hf_your-huggingface-key-here
```

### 4. Run the System

The system will automatically load the `.env` file:

```bash
python main.py
```

## Supported LLM Providers

### Anthropic (Claude) - **Currently Active**

**Required for:** The entire multi-agent system

**Get your API key:**
1. Visit: https://console.anthropic.com/
2. Sign up or log in
3. Go to API Keys section
4. Create a new key
5. Copy and paste into `.env`:
   ```
   ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
   ```

**Usage in system:**
- Orchestrator Agent uses Claude for intent recognition
- Research Agent uses Claude for reasoning and tool use
- All agents inherit Claude as their LLM brain

### OpenAI (GPT) - **Future Support**

**Get your API key:**
1. Visit: https://platform.openai.com/api-keys
2. Sign up or log in
3. Create new secret key
4. Copy and paste into `.env`:
   ```
   OPENAI_API_KEY=sk-xxxxxxxxxxxxx
   ```

**Future use cases:**
- Alternative LLM backend for agents
- Embeddings for semantic search
- Multi-model comparison

### Groq - **Future Support**

**Get your API key:**
1. Visit: https://console.groq.com/
2. Sign up or log in
3. Create API key
4. Copy and paste into `.env`:
   ```
   GROQ_API_KEY=gsk_xxxxxxxxxxxxx
   ```

**Future use cases:**
- Ultra-fast inference for simple tasks
- Cost-effective alternative for high-volume queries
- Mix of models for different agent types

### HuggingFace - **Future Support**

**Get your API key:**
1. Visit: https://huggingface.co/settings/tokens
2. Sign up or log in
3. Create new access token
4. Copy and paste into `.env`:
   ```
   HUGGINGFACE_API_KEY=hf_xxxxxxxxxxxxx
   ```

**Future use cases:**
- Open-source model alternatives
- Specialized models for specific tasks
- Local model deployment

## Environment File Structure

### Complete `.env` Template

```bash
# =============================================================================
# ANTHROPIC (Claude) - Required
# =============================================================================
# Get your key: https://console.anthropic.com/
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Optional: Specify Claude model version
# Default: claude-sonnet-4-5-20250929
CLAUDE_MODEL=claude-sonnet-4-5-20250929

# =============================================================================
# OPENAI (GPT) - Optional (Future)
# =============================================================================
# Get your key: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-your-key-here

# Optional: Specify GPT model
OPENAI_MODEL=gpt-4

# =============================================================================
# GROQ - Optional (Future)
# =============================================================================
# Get your key: https://console.groq.com/
GROQ_API_KEY=gsk-your-key-here

# Optional: Specify Groq model
GROQ_MODEL=mixtral-8x7b-32768

# =============================================================================
# HUGGINGFACE - Optional (Future)
# =============================================================================
# Get your key: https://huggingface.co/settings/tokens
HUGGINGFACE_API_KEY=hf_your-key-here

# Optional: Specify model from HuggingFace Hub
HUGGINGFACE_MODEL=meta-llama/Llama-2-70b-chat-hf

# =============================================================================
# SYSTEM CONFIGURATION
# =============================================================================
# Database path for memory storage
DB_PATH=data/memory.db

# Maximum iterations for agent loops
MAX_AGENT_ITERATIONS=15

# Enable verbose logging
VERBOSE=true

# =============================================================================
# FUTURE: EXTERNAL INTEGRATIONS
# =============================================================================
# Google APIs (for Phase 5 - Writing Agent)
# GOOGLE_CLIENT_ID=
# GOOGLE_CLIENT_SECRET=
# GOOGLE_REFRESH_TOKEN=

# Search APIs (for enhanced Research Agent)
# SERPAPI_KEY=
# GOOGLE_MAPS_API_KEY=
# YELP_API_KEY=
```

## Security Best Practices

### ✅ DO:

1. **Keep `.env` file local** - Never commit it to Git
   ```bash
   # Verify .env is in .gitignore
   grep .env .gitignore
   ```

2. **Use different keys for dev/prod**
   ```bash
   # Development
   .env

   # Production
   .env.production
   ```

3. **Rotate keys regularly**
   - Set calendar reminders to rotate API keys
   - Revoke old keys after rotation

4. **Set appropriate permissions**
   ```bash
   chmod 600 .env  # Read/write for owner only
   ```

### ❌ DON'T:

1. **Never commit `.env` to Git**
2. **Never share API keys in screenshots**
3. **Never hardcode keys in source code**
4. **Don't use production keys for testing**

## Verification

### Check Environment Variables Are Loaded

```bash
# Start Python
python

# In Python shell:
>>> import os
>>> from dotenv import load_dotenv
>>> load_dotenv()
True
>>> os.getenv('ANTHROPIC_API_KEY')
'sk-ant-...'  # Should show your key
>>> exit()
```

### Test the System

```bash
# Run the test script
python test_system.py

# Should show:
# ✅ Core types imported
# ✅ Base agent imported
# ✅ Orchestrator imported
# ✅ Research agent imported
# ✅ Memory store initialized
```

### Verify API Key Works

```bash
# Run the main application
python main.py

# If successful, you'll see:
# 🤖 Virtual Assistant - Multi-Agent System
# Available capabilities: ...
```

## Troubleshooting

### Error: "ANTHROPIC_API_KEY environment variable not set"

**Solution:**
```bash
# 1. Check .env file exists
ls -la .env

# 2. Check .env has the key
cat .env | grep ANTHROPIC_API_KEY

# 3. Make sure no extra spaces
# Wrong:  ANTHROPIC_API_KEY = sk-ant-...
# Right:  ANTHROPIC_API_KEY=sk-ant-...

# 4. Try running with explicit load
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('ANTHROPIC_API_KEY'))"
```

### Error: "API key invalid"

**Solution:**
1. Verify key is correct (copy-paste from console)
2. Check for extra spaces or newlines
3. Ensure key hasn't been revoked
4. Try creating a new key

### Error: "python-dotenv not installed"

**Solution:**
```bash
pip install python-dotenv
```

## Multi-Provider Configuration (Future)

When multi-provider support is added, you'll be able to configure which LLM each agent uses:

### Future Configuration Example

```python
# config/agent_models.yaml (Future)
orchestrator:
  primary: anthropic/claude-sonnet-4-5
  fallback: openai/gpt-4

research_agent:
  primary: groq/mixtral-8x7b  # Fast for research
  fallback: anthropic/claude-haiku

feedback_agent:
  primary: anthropic/claude-haiku  # Cheap for simple tasks

writing_agent:
  primary: anthropic/claude-sonnet-4-5  # Best quality
  fallback: openai/gpt-4
```

### Cost Optimization Strategy

```bash
# Use different models for different tasks
FAST_MODEL=groq/mixtral-8x7b          # Simple queries
BALANCED_MODEL=anthropic/claude-haiku  # Most tasks
QUALITY_MODEL=anthropic/claude-sonnet  # Complex reasoning
```

## Integration with Python Code

The system uses `python-dotenv` to automatically load variables:

```python
# In config/settings.py
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Access variables
api_key = os.getenv("ANTHROPIC_API_KEY")
model = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5-20250929")
```

## Environment File Locations

The system looks for `.env` files in this order:

1. **Project root** - `.env` (highest priority)
2. **User home** - `~/.agentex.env` (future)
3. **System** - `/etc/agentex/.env` (future)

## Updating Configuration

### Change Model

```bash
# In .env file
CLAUDE_MODEL=claude-opus-4-5-20250929  # Switch to Opus for better quality

# Or temporarily via command line
CLAUDE_MODEL=claude-haiku python main.py  # One-time override
```

### Enable Verbose Logging

```bash
# In .env file
VERBOSE=true
```

### Change Database Location

```bash
# In .env file
DB_PATH=/path/to/custom/location/memory.db
```

## Next Steps

1. ✅ Create your `.env` file from `.env.example`
2. ✅ Add your Anthropic API key (required)
3. ✅ Optionally add other provider keys for future use
4. ✅ Test the system with `python test_system.py`
5. ✅ Start using the assistant with `python main.py`

## Getting Help

**API Key Issues:**
- Anthropic: https://docs.anthropic.com/
- OpenAI: https://platform.openai.com/docs
- Groq: https://console.groq.com/docs
- HuggingFace: https://huggingface.co/docs

**System Issues:**
- Check `test_system.py` output
- Review error messages carefully
- Ensure all dependencies installed: `pip install -r requirements.txt`

---

**Pro Tip:** Keep a backup copy of your `.env` file in a secure password manager (1Password, LastPass, etc.) so you don't lose your API keys!
