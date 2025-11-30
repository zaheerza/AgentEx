# Virtual Assistant Multi-Agent System - Architecture Plan

## Vision

A personal virtual assistant powered by an orchestrator agent that coordinates specialized sub-agents to manage different aspects of life and productivity.

## System Overview

```
┌─────────────────────────────────────────────────────────┐
│                    USER INTERFACE                        │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              ORCHESTRATOR AGENT                          │
│  - Routes tasks to appropriate agents                    │
│  - Manages agent lifecycle                               │
│  - Aggregates results                                    │
│  - Maintains conversation context                        │
└────┬────────────┬────────────┬──────────────┬───────────┘
     │            │            │              │
     ▼            ▼            ▼              ▼
┌─────────┐  ┌─────────┐  ┌─────────┐  ┌──────────────┐
│Research │  │Feedback │  │  Deals  │  │   Content    │
│ Agent   │  │ Tracker │  │  Agent  │  │Writing Agent │
└─────────┘  └─────────┘  └─────────┘  └──────────────┘
     │            │            │              │
     └────────────┴────────────┴──────────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │   SHARED MEMORY LAYER  │
         │  - Vector DB           │
         │  - SQLite              │
         │  - File Storage        │
         └────────────────────────┘
```

---

## 1. Core Architecture Components

### 1.1 Orchestrator Agent

**Responsibilities:**
- Receive user requests and determine intent
- Route tasks to appropriate sub-agents
- Manage multi-step workflows across agents
- Aggregate and synthesize results from multiple agents
- Maintain conversation context and session state
- Handle error recovery and fallbacks

**Key Capabilities:**
```python
class OrchestratorAgent:
    - analyze_intent(user_input) -> Intent
    - route_to_agent(intent) -> Agent
    - coordinate_multi_agent_task(task) -> Result
    - synthesize_results(agent_results) -> Response
    - maintain_context(conversation_history)
```

**Decision Making:**
```
User: "Find me Italian restaurants in downtown and check for deals"

Orchestrator analyzes:
1. Primary intent: Find restaurants (→ Research Agent)
2. Secondary intent: Find deals (→ Deals Agent)
3. Execution: Run both in parallel
4. Synthesize: Combine results into unified response
```

### 1.2 Agent Framework (Base Classes)

**BaseAgent Interface:**
```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class AgentCapability:
    """Describes what an agent can do"""
    name: str
    description: str
    keywords: List[str]  # Intent matching
    required_inputs: List[str]
    output_schema: Dict[str, Any]

@dataclass
class Task:
    """Task passed to an agent"""
    task_id: str
    description: str
    parameters: Dict[str, Any]
    context: Dict[str, Any]  # Shared context from orchestrator
    priority: int = 1

@dataclass
class AgentResult:
    """Result from agent execution"""
    task_id: str
    agent_name: str
    success: bool
    data: Any
    metadata: Dict[str, Any]
    error: Optional[str] = None

class BaseAgent(ABC):
    """Base class all task agents inherit from"""

    def __init__(self, name: str, api_key: str):
        self.name = name
        self.client = anthropic.Anthropic(api_key=api_key)
        self.capabilities = self._define_capabilities()
        self.tools = self._define_tools()
        self.memory = AgentMemory(agent_name=name)

    @abstractmethod
    def _define_capabilities(self) -> List[AgentCapability]:
        """Define what this agent can do"""
        pass

    @abstractmethod
    def _define_tools(self) -> List[Dict[str, Any]]:
        """Define tools this agent can use"""
        pass

    @abstractmethod
    def _execute_tool(self, tool_name: str, tool_input: Dict) -> str:
        """Execute a tool and return result"""
        pass

    def execute(self, task: Task) -> AgentResult:
        """Main execution method - orchestrator calls this"""
        try:
            result = self._run_agent_loop(task)
            return AgentResult(
                task_id=task.task_id,
                agent_name=self.name,
                success=True,
                data=result,
                metadata={"iterations": self._iteration_count}
            )
        except Exception as e:
            return AgentResult(
                task_id=task.task_id,
                agent_name=self.name,
                success=False,
                data=None,
                metadata={},
                error=str(e)
            )

    def _run_agent_loop(self, task: Task) -> Any:
        """Internal agent execution loop (ReAct pattern)"""
        # Implementation of observe-think-act loop
        pass

    def can_handle(self, intent: str) -> float:
        """Returns confidence score (0-1) if agent can handle intent"""
        pass
```

---

## 2. First Implementation: Research Agent

**Purpose:** Research places to visit, events to attend, restaurants

**Capabilities:**
```python
capabilities = [
    AgentCapability(
        name="find_restaurants",
        description="Search for restaurants by cuisine, location, rating",
        keywords=["restaurant", "food", "eat", "dining", "cuisine"],
        required_inputs=["location"],
        output_schema={
            "restaurants": [
                {
                    "name": str,
                    "cuisine": str,
                    "location": str,
                    "rating": float,
                    "price_range": str,
                    "highlights": List[str]
                }
            ]
        }
    ),
    AgentCapability(
        name="find_events",
        description="Search for events by type, date, location",
        keywords=["event", "concert", "show", "festival", "activity"],
        required_inputs=["location", "date_range"],
        output_schema={...}
    ),
    AgentCapability(
        name="find_places",
        description="Research places to visit (attractions, parks, etc)",
        keywords=["visit", "attraction", "tourist", "place", "sightseeing"],
        required_inputs=["location"],
        output_schema={...}
    )
]
```

**Tools:**
```python
tools = [
    {
        "name": "search_web",
        "description": "Search the web for current information",
        "input_schema": {...}
    },
    {
        "name": "search_google_maps",
        "description": "Search Google Maps for places",
        "input_schema": {...}
    },
    {
        "name": "get_reviews",
        "description": "Get reviews for a specific place",
        "input_schema": {...}
    },
    {
        "name": "check_hours",
        "description": "Check business hours and availability",
        "input_schema": {...}
    },
    {
        "name": "save_recommendation",
        "description": "Save a recommendation to memory for future reference",
        "input_schema": {...}
    }
]
```

**Example Flow:**
```
User → Orchestrator: "Find me Italian restaurants in downtown Seattle"

Orchestrator → Research Agent:
  Task(
    description="Find Italian restaurants in downtown Seattle",
    parameters={
      "cuisine": "Italian",
      "location": "downtown Seattle",
      "filters": {"open_now": True}
    }
  )

Research Agent:
  1. search_web("Italian restaurants downtown Seattle")
  2. search_google_maps("Italian restaurants", location="downtown Seattle")
  3. get_reviews(restaurant_name) for top candidates
  4. Synthesize results
  5. save_recommendation(results)
  6. Return formatted list

Research Agent → Orchestrator: AgentResult(
  data={
    "restaurants": [
      {
        "name": "Cafe Juanita",
        "cuisine": "Italian",
        "rating": 4.7,
        "price": "$$$",
        "highlights": ["Fresh pasta", "Wine selection"],
        "address": "..."
      },
      ...
    ],
    "count": 5
  }
)

Orchestrator → User: Formatted response with recommendations
```

---

## 3. Future Agents (Roadmap)

### 3.1 Feedback Tracker Agent

**Purpose:** Track experiences and collect feedback after visits

**Capabilities:**
- Prompt for feedback after visiting a place
- Record structured feedback (ratings, notes, photos)
- Analyze patterns in preferences
- Update recommendations based on feedback

**Tools:**
- `create_feedback_request()` - Schedule follow-up
- `record_feedback()` - Save user feedback
- `analyze_preferences()` - Learn from history
- `update_recommendation_weights()` - Improve future suggestions

**Workflow:**
```
After user visits a restaurant:
1. Agent sends follow-up (next day)
2. Collects: rating, liked/disliked, would return?, notes
3. Stores in memory with tags
4. Updates user preference profile
5. Shares insights with Research Agent
```

### 3.2 Deals Agent

**Purpose:** Find deals, discounts, and special offers

**Capabilities:**
- Monitor deal sites (Groupon, LivingSocial, etc.)
- Track price drops on saved places
- Find promotional codes
- Alert on time-sensitive offers

**Tools:**
- `search_deals()` - Search deal aggregators
- `monitor_price()` - Track price changes
- `check_promotions()` - Find current promos
- `set_alert()` - Create deal alerts

### 3.3 Content Writing Agent

**Purpose:** Transform bullet points and references into coherent articles

**Capabilities:**
- Fetch content from Google Docs/Keep
- Synthesize multiple sources
- Generate drafts in different styles (article, blog post, summary)
- Maintain consistent voice

**Tools:**
- `fetch_google_doc()` - Read Google Docs
- `fetch_google_keep()` - Read Keep notes
- `extract_bullet_points()` - Parse structured input
- `generate_outline()` - Create content structure
- `write_section()` - Draft content sections
- `save_to_google_doc()` - Save final output

**Integration Requirements:**
- Google Drive API (OAuth)
- Google Keep API
- Template system for different content types

---

## 4. Data & Memory Architecture

### 4.1 Shared Memory Layer

**Purpose:** Centralized data store accessible by all agents

**Components:**

```python
class SharedMemory:
    """Centralized memory system"""

    def __init__(self):
        self.vector_db = ChromaDB()      # For semantic search
        self.sql_db = SQLite()           # For structured data
        self.file_storage = FileSystem() # For documents/media

    # User preferences and history
    def get_user_preferences(self, category: str) -> Dict
    def update_user_preferences(self, data: Dict)

    # Agent shared knowledge
    def store_finding(self, agent_name: str, data: Dict)
    def search_similar(self, query: str, agent_scope: str = None)

    # Feedback and learning
    def store_feedback(self, item_id: str, feedback: Dict)
    def get_feedback_history(self, filters: Dict)

    # Session context
    def store_context(self, session_id: str, context: Dict)
    def get_context(self, session_id: str) -> Dict
```

**Database Schema:**

```sql
-- Recommendations (restaurants, events, places)
CREATE TABLE recommendations (
    id TEXT PRIMARY KEY,
    type TEXT,  -- 'restaurant', 'event', 'place'
    name TEXT,
    location TEXT,
    metadata JSON,
    source_agent TEXT,
    created_at TIMESTAMP,
    visited BOOLEAN DEFAULT FALSE
);

-- User feedback
CREATE TABLE feedback (
    id TEXT PRIMARY KEY,
    recommendation_id TEXT,
    rating INTEGER,
    notes TEXT,
    liked TEXT[],  -- Array of liked aspects
    disliked TEXT[],
    would_return BOOLEAN,
    created_at TIMESTAMP,
    FOREIGN KEY (recommendation_id) REFERENCES recommendations(id)
);

-- User preferences (learned over time)
CREATE TABLE preferences (
    id TEXT PRIMARY KEY,
    category TEXT,
    key TEXT,
    value TEXT,
    confidence FLOAT,  -- How confident we are in this preference
    updated_at TIMESTAMP
);

-- Deals and offers
CREATE TABLE deals (
    id TEXT PRIMARY KEY,
    recommendation_id TEXT,
    description TEXT,
    discount_amount TEXT,
    valid_until TIMESTAMP,
    source_url TEXT,
    created_at TIMESTAMP
);

-- Agent tasks and results (for auditing)
CREATE TABLE agent_executions (
    id TEXT PRIMARY KEY,
    task_id TEXT,
    agent_name TEXT,
    input JSON,
    output JSON,
    success BOOLEAN,
    duration_ms INTEGER,
    created_at TIMESTAMP
);
```

**Vector Store Usage:**
```python
# Store embeddings for semantic search
vector_db.add_documents([
    {
        "id": "rest_001",
        "text": "Italian restaurant with amazing pasta and wine selection",
        "metadata": {"type": "restaurant", "cuisine": "Italian"}
    }
])

# Semantic search
results = vector_db.similarity_search(
    "find me places with great wine",
    filter={"type": "restaurant"}
)
```

### 4.2 Agent-Specific Memory

Each agent maintains its own working memory:
```python
class AgentMemory:
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.short_term = []  # Current task context
        self.learned_patterns = {}  # Agent-specific learnings

    def remember_task_result(self, task: Task, result: Any):
        """Store successful task patterns"""

    def recall_similar_tasks(self, task: Task) -> List[Any]:
        """Find similar past tasks for context"""
```

---

## 5. Communication Protocol

### 5.1 Orchestrator → Agent Communication

**Task Assignment:**
```python
task = Task(
    task_id="task_123",
    description="Find Italian restaurants in Seattle",
    parameters={
        "cuisine": "Italian",
        "location": "Seattle",
        "max_results": 5
    },
    context={
        "user_id": "user_456",
        "session_id": "session_789",
        "user_preferences": {...},
        "conversation_history": [...]
    },
    priority=1
)

result = agent.execute(task)
```

**Agent Response:**
```python
AgentResult(
    task_id="task_123",
    agent_name="research_agent",
    success=True,
    data={
        "restaurants": [...],
        "metadata": {
            "search_duration_ms": 3500,
            "sources": ["google_maps", "yelp"]
        }
    },
    metadata={
        "iterations": 5,
        "tools_used": ["search_web", "get_reviews"],
        "confidence": 0.85
    }
)
```

### 5.2 Inter-Agent Communication

Agents can request information from other agents via orchestrator:

```python
class BaseAgent:
    def request_from_agent(self, agent_name: str, request: Dict) -> Any:
        """Request data from another agent via orchestrator"""
        return self.orchestrator.route_inter_agent_request(
            from_agent=self.name,
            to_agent=agent_name,
            request=request
        )

# Example: Deals Agent querying Research Agent
saved_restaurants = self.request_from_agent(
    "research_agent",
    {"action": "get_saved_items", "type": "restaurant"}
)
```

---

## 6. Integration Points

### 6.1 External APIs

**Google Services:**
```python
class GoogleIntegration:
    """Handle all Google API integrations"""

    def __init__(self, credentials_path: str):
        self.docs_client = GoogleDocsClient(credentials_path)
        self.keep_client = GoogleKeepClient(credentials_path)
        self.calendar_client = GoogleCalendarClient(credentials_path)

    def fetch_doc(self, doc_id: str) -> Dict
    def fetch_keep_notes(self, labels: List[str]) -> List[Dict]
    def create_doc(self, title: str, content: str) -> str
    def add_calendar_event(self, event: Dict) -> str
```

**Search & Maps:**
- Google Maps API (places, reviews, hours)
- SerpAPI (web search results)
- Yelp Fusion API (restaurant details)

**Deals & Promotions:**
- Custom web scrapers for deal sites
- RSS feeds from promotional sites

### 6.2 Authentication

```python
# OAuth flow for Google services
# API keys for other services stored in .env

class CredentialManager:
    def get_google_credentials(self) -> Credentials
    def get_api_key(self, service: str) -> str
    def refresh_token(self, service: str) -> bool
```

---

## 7. Project File Structure

```
AgentEx/
├── README.md
├── ARCHITECTURE_PLAN.md (this file)
├── QUICKSTART.md
├── requirements.txt
│
├── config/
│   ├── __init__.py
│   ├── settings.py          # Configuration
│   └── credentials.json     # API keys (gitignored)
│
├── core/
│   ├── __init__.py
│   ├── base_agent.py        # BaseAgent abstract class
│   ├── orchestrator.py      # OrchestratorAgent
│   ├── types.py             # Task, AgentResult, etc.
│   └── agent_registry.py    # Agent discovery/registration
│
├── agents/
│   ├── __init__.py
│   ├── research_agent.py    # First implementation
│   ├── feedback_agent.py    # Future
│   ├── deals_agent.py       # Future
│   └── writing_agent.py     # Future
│
├── memory/
│   ├── __init__.py
│   ├── shared_memory.py     # Shared memory layer
│   ├── vector_store.py      # Vector DB wrapper
│   ├── sql_store.py         # SQLite wrapper
│   └── schemas.sql          # Database schemas
│
├── integrations/
│   ├── __init__.py
│   ├── google_integration.py
│   ├── maps_api.py
│   ├── search_api.py
│   └── deals_scrapers.py
│
├── tools/
│   ├── __init__.py
│   ├── web_search.py
│   ├── maps_search.py
│   └── file_operations.py
│
├── ui/
│   ├── __init__.py
│   ├── cli.py               # Command-line interface
│   └── web_ui.py            # Future: web interface
│
├── tests/
│   ├── test_orchestrator.py
│   ├── test_agents/
│   │   └── test_research_agent.py
│   └── test_memory.py
│
├── examples/
│   ├── simple_agent.py      # Existing examples
│   ├── research_agent.py
│   └── code_agent.py
│
└── data/
    ├── memory.db            # SQLite database
    ├── vector_store/        # Chroma DB files
    └── user_data/           # User-specific data
```

---

## 8. Implementation Phases

### Phase 1: Foundation (Start Here)
**Goal:** Get orchestrator + research agent working

**Tasks:**
1. ✅ Create base agent framework
   - `core/base_agent.py` - Abstract base class
   - `core/types.py` - Data structures

2. ✅ Build orchestrator agent
   - `core/orchestrator.py` - Main coordinator
   - Intent recognition
   - Single agent routing

3. ✅ Implement research agent (restaurants only)
   - `agents/research_agent.py`
   - Tools: web search, save results
   - Basic capability: find restaurants

4. ✅ Set up basic memory
   - `memory/sql_store.py` - SQLite for recommendations
   - Simple storage/retrieval

5. ✅ Create CLI interface
   - `ui/cli.py` - Basic command line interaction

**Deliverable:** Working system where you can ask for restaurant recommendations

### Phase 2: Enhanced Research
**Goal:** Full research agent capabilities

**Tasks:**
1. Add events search capability
2. Add places/attractions search
3. Integrate Google Maps API
4. Add vector store for semantic search
5. Improve result ranking and filtering

**Deliverable:** Comprehensive research across all categories

### Phase 3: Feedback Loop
**Goal:** Add feedback tracking agent

**Tasks:**
1. Implement feedback agent
2. Add feedback prompting system
3. Build preference learning
4. Connect feedback to research agent

**Deliverable:** System learns your preferences over time

### Phase 4: Deals Agent
**Goal:** Add deal finding capabilities

**Tasks:**
1. Implement deals agent
2. Build web scrapers for deal sites
3. Add price monitoring
4. Create alert system

**Deliverable:** Automatic deal notifications

### Phase 5: Content Writing
**Goal:** Add content creation capabilities

**Tasks:**
1. Implement writing agent
2. Integrate Google Docs/Keep APIs
3. Build content templates
4. Add multi-source synthesis

**Deliverable:** Turn notes into polished content

### Phase 6: Intelligence & Polish
**Goal:** Make system smarter and more autonomous

**Tasks:**
1. Multi-agent collaboration
2. Proactive suggestions
3. Web UI
4. Mobile notifications
5. Advanced preference learning

---

## 9. Key Design Decisions

### 9.1 Why Orchestrator Pattern?

**Advantages:**
- ✅ Clean separation of concerns
- ✅ Easy to add new agents
- ✅ Centralized context management
- ✅ Single point for user interaction
- ✅ Agents can be developed/tested independently

**vs Alternative (Direct Agent Access):**
- ❌ User needs to know which agent to call
- ❌ Context sharing is harder
- ❌ Multi-agent workflows are complex

### 9.2 Shared Memory vs Agent-Specific

**Shared Memory For:**
- User preferences
- Recommendations and feedback
- Cross-agent data (deals on saved restaurants)

**Agent-Specific Memory For:**
- Task execution patterns
- Tool usage optimization
- Agent-specific learnings

### 9.3 Synchronous vs Asynchronous Execution

**Phase 1:** Synchronous (simpler)
```python
result = agent.execute(task)  # Blocks until complete
```

**Future:** Async for parallel execution
```python
results = await orchestrator.execute_parallel([
    research_task,
    deals_task
])
```

### 9.4 Tool Sharing

Common tools (web_search, file operations) are:
- Defined in `tools/` directory
- Imported by agents that need them
- Executed in agent context (for proper memory attribution)

---

## 10. Example User Interactions

### Simple Query
```
User: "Find me sushi restaurants in downtown"

Orchestrator:
  ├─ Identifies: Research task, restaurant category
  ├─ Routes to: Research Agent
  └─ Context: location preference, rating threshold

Research Agent:
  ├─ search_web("sushi downtown")
  ├─ search_google_maps(cuisine="sushi")
  ├─ get_reviews(top_5)
  └─ Returns: 5 ranked restaurants

Orchestrator → User: "Here are 5 sushi restaurants..."
```

### Complex Multi-Agent Query
```
User: "Find me a romantic Italian restaurant for Friday night,
       check if there are any deals, and remind me to get feedback
       after I go"

Orchestrator:
  ├─ Identifies: Research + Deals + Feedback scheduling
  ├─ Routes to: Multiple agents in sequence
  │   ├─ Research Agent: Find romantic Italian restaurants
  │   ├─ Deals Agent: Check for deals on those restaurants
  │   └─ Feedback Agent: Schedule reminder for Saturday
  └─ Synthesizes: Combined response with restaurant, deal info, reminder set

User receives: Restaurant recommendation with deal + confirmation of reminder
```

### Proactive Agent Behavior (Future)
```
System (Feedback Agent):
  "Hi! You visited Cafe Juanita last night. How was it?"

User: "Great! Loved the pasta"

Feedback Agent:
  ├─ Stores: positive feedback, highlight="pasta"
  ├─ Updates: user preference weight for Italian +10%
  └─ Notifies Research Agent: Update recommendation weights

Next time user asks for restaurants, Italian gets higher priority
```

---

## 11. Testing Strategy

### Unit Tests
```python
# Test individual agent capabilities
def test_research_agent_find_restaurants():
    agent = ResearchAgent(api_key=test_key)
    task = Task(
        description="Find Italian restaurants",
        parameters={"cuisine": "Italian", "location": "Seattle"}
    )
    result = agent.execute(task)
    assert result.success
    assert len(result.data['restaurants']) > 0
```

### Integration Tests
```python
# Test orchestrator + agent coordination
def test_orchestrator_routes_correctly():
    orchestrator = OrchestratorAgent()
    response = orchestrator.handle_input(
        "Find me restaurants"
    )
    assert response.agent_used == "research_agent"
```

### End-to-End Tests
```python
# Test full user flows
def test_full_restaurant_search_flow():
    # Simulate: User asks → gets results → provides feedback
    pass
```

---

## 12. Open Questions & Decisions Needed

1. **User Authentication:**
   - Single user vs multi-user system?
   - How to handle Google OAuth tokens?

2. **Persistence:**
   - Where to store database file (local vs cloud)?
   - Backup strategy?

3. **Cost Management:**
   - Token usage limits per agent?
   - Caching strategy for repeated queries?

4. **Notification System:**
   - How should feedback agent remind users? (Email? SMS? In-app?)

5. **Privacy:**
   - What data do we store?
   - How long to retain feedback/preferences?

---

## Next Steps

**Immediate (Phase 1 Implementation):**

1. Create base framework structure
2. Implement `BaseAgent` abstract class
3. Build `OrchestratorAgent` with basic routing
4. Implement `ResearchAgent` (restaurants only)
5. Set up SQLite storage
6. Create simple CLI
7. Test end-to-end flow

**After user approval of this plan, we'll start implementing Phase 1!**

---

## Summary

This architecture provides:
- ✅ Scalable multi-agent system
- ✅ Clean separation of concerns
- ✅ Easy to add new agents
- ✅ Centralized memory and learning
- ✅ Extensible tool framework
- ✅ Clear path from MVP to full system

**Starting point:** Orchestrator + Research Agent (restaurants)
**Growth path:** Add agents incrementally as needed
**End state:** Fully autonomous personal assistant managing multiple life domains
