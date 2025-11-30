# Virtual Assistant - Multi-Agent System

A personal AI-powered virtual assistant built with a multi-agent architecture. The system uses Claude to power specialized agents that help manage different aspects of your life.

## 🎯 Vision

An orchestrated multi-agent system where:
- An **Orchestrator Agent** coordinates specialized task agents
- Each agent focuses on specific capabilities (research, feedback, deals, content creation)
- Agents share memory and learn from your preferences over time
- Easy to extend with new agents as needed

## ✅ Phase 1: Foundation (Implemented)

### What's Working

**Core Framework:**
- ✅ Base Agent class that all agents inherit from
- ✅ Standardized Task and AgentResult types
- ✅ ReAct pattern (Reasoning + Acting) implementation
- ✅ Tool-based architecture

**Orchestrator Agent:**
- ✅ Routes user queries to appropriate agents
- ✅ Intent recognition and agent matching
- ✅ Parameter extraction from natural language
- ✅ Result formatting and presentation
- ✅ Conversation context management

**Research Agent:**
- ✅ Restaurant search by cuisine, location, price, rating
- ✅ Mock data for testing (ready for real API integration)
- ✅ Result ranking and filtering
- ✅ Save recommendations to memory

**Memory System:**
- ✅ SQLite database for persistent storage
- ✅ Stores recommendations, feedback, preferences
- ✅ Statistics and history tracking
- ✅ Audit trail of agent executions

**CLI Interface:**
- ✅ Interactive command-line interface
- ✅ Natural language input
- ✅ Commands: /stats, /history, /clear, /quit
- ✅ Formatted output

## 🚀 Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set up your API keys (choose one method)

# Method 1: Using .env file (Recommended)
cp .env.example .env
# Then edit .env and add your Groq API key

# Method 2: Environment variable
export GROQ_API_KEY='your-groq-api-key'
```

**📖 For detailed setup instructions, see [ENV_SETUP.md](ENV_SETUP.md)**

### 2. Run the Assistant

```bash
python main.py
```

### 3. Try It Out

```
You: Find Italian restaurants in downtown Seattle

You: Show me cheap sushi places

You: Find highly rated Mexican food

You: /stats    # View system statistics
You: /history  # See saved recommendations
```

## 📁 Project Structure

```
AgentEx/
├── core/                   # Core framework
│   ├── base_agent.py      # Abstract base class for all agents
│   ├── orchestrator.py    # Main coordinator agent
│   └── types.py           # Shared data types
│
├── agents/                 # Task-specific agents
│   └── research_agent.py  # Restaurant/events/places research
│
├── memory/                 # Persistence layer
│   ├── sql_store.py       # SQLite storage
│   └── schemas.sql        # Database schema
│
├── ui/                     # User interfaces
│   └── cli.py             # Command-line interface
│
├── config/                 # Configuration
│   └── settings.py        # Settings management
│
├── data/                   # Data storage (created at runtime)
│   └── memory.db          # SQLite database
│
├── main.py                # Entry point
├── test_system.py         # System tests
└── requirements.txt       # Dependencies
```

## 🏗️ Architecture

### Agent Communication Flow

```
User Input
    ↓
Orchestrator Agent
├─ Analyzes intent
├─ Extracts parameters
├─ Finds best agent
└─ Creates task
    ↓
Research Agent (or other agents)
├─ Receives task
├─ Uses tools (search, save, etc.)
├─ Executes ReAct loop
└─ Returns result
    ↓
Orchestrator Agent
├─ Formats result
└─ Presents to user
```

### Base Agent Pattern

All agents inherit from `BaseAgent` and implement:

```python
class MyAgent(BaseAgent):
    def _define_capabilities(self) -> List[AgentCapability]:
        """What can this agent do?"""

    def _define_tools(self) -> List[ToolDefinition]:
        """What tools can it use?"""

    def _define_system_prompt(self) -> str:
        """How should it behave?"""

    def _execute_tool(self, tool_name, tool_input):
        """Execute tool implementations"""
```

### Memory Schema

```sql
recommendations  # Saved restaurants, events, places
feedback        # User ratings and notes
preferences     # Learned preferences over time
deals           # Special offers and discounts
agent_executions # Audit trail
```

## 🔮 Future Phases

### Phase 2: Enhanced Research
- [ ] Events search capability
- [ ] Places/attractions research
- [ ] Google Maps API integration
- [ ] Vector database for semantic search
- [ ] Improved result ranking

### Phase 3: Feedback Agent
- [ ] Post-visit feedback collection
- [ ] Preference learning
- [ ] Recommendation improvement
- [ ] Proactive follow-ups

### Phase 4: Deals Agent
- [ ] Deal aggregator integration
- [ ] Price monitoring
- [ ] Special offers tracking
- [ ] Time-sensitive alerts

### Phase 5: Content Writing Agent
- [ ] Google Docs integration
- [ ] Google Keep integration
- [ ] Bullet points → articles
- [ ] Multi-source synthesis
- [ ] Different content styles

### Phase 6: Advanced Features
- [ ] Multi-agent workflows
- [ ] Proactive suggestions
- [ ] Web UI
- [ ] Mobile notifications
- [ ] Voice interface
- [ ] Calendar integration

## 🔧 Extending the System

### Adding a New Agent

1. **Create agent file** in `agents/`:

```python
from core.base_agent import BaseAgent
from core.types import AgentCapability, ToolDefinition

class MyNewAgent(BaseAgent):
    def __init__(self, api_key: str):
        super().__init__(name="my_agent", api_key=api_key)

    def _define_capabilities(self):
        return [
            AgentCapability(
                name="my_capability",
                description="What I can do",
                keywords=["trigger", "words"],
                required_inputs=["param1"],
                examples=["Example query"]
            )
        ]

    def _define_tools(self):
        return [
            ToolDefinition(
                name="my_tool",
                description="What this tool does",
                input_schema={...}
            )
        ]

    def _define_system_prompt(self):
        return "You are an agent that..."

    def _execute_tool(self, tool_name, tool_input):
        if tool_name == "my_tool":
            # Implementation
            return "result"
```

2. **Register in CLI** (`ui/cli.py`):

```python
from agents.my_new_agent import MyNewAgent

# In _register_agents():
my_agent = MyNewAgent(api_key=self.settings.anthropic_api_key)
self.orchestrator.register_agent(my_agent)
```

3. **Test it:**

```bash
python main.py
You: [trigger your new agent with a query]
```

## 🧪 Testing

```bash
# Run system tests
python test_system.py

# Check imports and memory
python -c "from core.orchestrator import OrchestratorAgent; print('OK')"
```

## 📊 Database Queries

View stored data directly:

```bash
sqlite3 data/memory.db

# View recommendations
SELECT name, type, location FROM recommendations;

# View feedback
SELECT * FROM feedback;

# View preferences
SELECT * FROM preferences;
```

## 🛠️ Configuration

Environment variables:

```bash
ANTHROPIC_API_KEY=your-key      # Required
CLAUDE_MODEL=claude-sonnet-4.5   # Optional
DB_PATH=data/memory.db          # Optional
MAX_AGENT_ITERATIONS=15         # Optional
VERBOSE=true                    # Optional
```

## 📖 Example Interactions

### Simple Query
```
You: Find Italian restaurants

Orchestrator:
  ├─ Identifies: Research task
  ├─ Routes to: Research Agent
  └─ Parameters: {cuisine: "Italian"}

Research Agent:
  ├─ search_restaurants(cuisine="Italian")
  ├─ Ranks by rating
  └─ Returns: Top 5 restaurants

Result: "I found 5 Italian restaurants..."
```

### Complex Query
```
You: Find cheap sushi near downtown with good ratings

Orchestrator:
  └─ Extracts: {
      cuisine: "sushi",
      location: "downtown",
      price_range: "$",
      min_rating: 4.0
    }

Research Agent:
  └─ Filtered search with all criteria

Result: Ranked list matching all filters
```

## 🔒 Privacy & Data

- All data stored locally in SQLite
- No data sent anywhere except Claude API for processing
- API key stored in environment (not in code)
- Database file in `.gitignore`

## 🤝 Contributing

See `ARCHITECTURE_PLAN.md` for detailed system design and future roadmap.

## 📝 License

This is an educational project demonstrating multi-agent AI systems.

## 🙏 Acknowledgments

Built with:
- [Anthropic Claude](https://www.anthropic.com/) - AI reasoning and tool use
- Python 3.x - Core implementation
- SQLite - Local data persistence

---

**Status:** Phase 1 Complete ✅
**Next:** Ready to add more agents or enhance existing capabilities!
