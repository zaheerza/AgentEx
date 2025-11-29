#!/usr/bin/env python3
"""
Quick test script for the multi-agent system.
"""

import os
import sys

# Test imports
print("Testing imports...")

try:
    from core.types import Task, AgentResult, AgentCapability
    print("✅ Core types imported")
except Exception as e:
    print(f"❌ Error importing core types: {e}")
    sys.exit(1)

try:
    from core.base_agent import BaseAgent
    print("✅ Base agent imported")
except Exception as e:
    print(f"❌ Error importing base agent: {e}")
    sys.exit(1)

try:
    from core.orchestrator import OrchestratorAgent
    print("✅ Orchestrator imported")
except Exception as e:
    print(f"❌ Error importing orchestrator: {e}")
    sys.exit(1)

try:
    from agents.research_agent import ResearchAgent
    print("✅ Research agent imported")
except Exception as e:
    print(f"❌ Error importing research agent: {e}")
    sys.exit(1)

try:
    from memory.sql_store import SQLMemoryStore
    print("✅ Memory store imported")
except Exception as e:
    print(f"❌ Error importing memory store: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("All imports successful! 🎉")
print("="*60)

# Test memory store
print("\nTesting memory store...")
try:
    memory = SQLMemoryStore(db_path="data/test_memory.db")
    print("✅ Memory store initialized")

    # Save a test recommendation
    rec_id = memory.save_recommendation(
        type="restaurant",
        data={
            "name": "Test Restaurant",
            "cuisine": "Italian",
            "location": "Seattle",
            "rating": 4.5
        }
    )
    print(f"✅ Saved test recommendation: {rec_id}")

    # Retrieve it
    recs = memory.get_recommendations(type="restaurant", limit=1)
    if recs and recs[0]['name'] == "Test Restaurant":
        print("✅ Retrieved test recommendation")
    else:
        print("❌ Failed to retrieve recommendation")

    # Get stats
    stats = memory.get_stats()
    print(f"✅ Memory stats: {stats}")

except Exception as e:
    print(f"❌ Memory store test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("Memory store test complete!")
print("="*60)

# Test agent capabilities
print("\nTesting agent capabilities...")

# Check if API key is set
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    print("⚠️  ANTHROPIC_API_KEY not set - skipping agent execution test")
    print("   Set it with: export ANTHROPIC_API_KEY='your-key'")
else:
    try:
        # Create research agent
        research_agent = ResearchAgent(api_key=api_key, memory_store=memory)
        print("✅ Research agent created")

        # Test capability matching
        score = research_agent.can_handle("find italian restaurants")
        print(f"✅ Capability matching works (score: {score:.2f})")

        # Create orchestrator
        orchestrator = OrchestratorAgent(api_key=api_key)
        orchestrator.register_agent(research_agent)
        print("✅ Orchestrator created and agent registered")

        print("\n✅ All tests passed! System is ready to use.")
        print("\nTo start the assistant, run:")
        print("  python main.py")

    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*60)
