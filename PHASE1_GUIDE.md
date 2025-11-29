# Phase 1: Getting Started with the Virtual Assistant

## What's Implemented

Phase 1 delivers a working multi-agent system with:

✅ **Orchestrator Agent** - Coordinates all sub-agents
✅ **Research Agent** - Finds restaurants based on your preferences
✅ **Memory System** - Saves recommendations for future reference
✅ **CLI Interface** - Simple command-line interaction

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up API Key

```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

Or create a `.env` file:
```
ANTHROPIC_API_KEY=your-api-key-here
```

### 3. Run the Assistant

```bash
python main.py
```

## Example Usage

### Finding Restaurants

```
You: Find Italian restaurants in downtown Seattle