"""
My First Agent - A Simple Autonomous AI Agent
==============================================
This file demonstrates the key components of an autonomous AI agent.

KEY COMPONENTS:
1. LLM Brain - The reasoning engine (Claude)
2. Tools - Actions the agent can take
3. Memory - Conversation history
4. Agent Loop - The observe-think-act cycle
"""

import anthropic
import json
import os
from typing import Any


# =============================================================================
# COMPONENT 1: TOOLS
# =============================================================================
# Tools give the agent the ability to interact with the world.
# Each tool has:
#   - name: identifier for the tool
#   - description: tells the LLM when to use it
#   - input_schema: defines the parameters

TOOLS = [
    {
        "name": "calculator",
        "description": "Perform mathematical calculations. Use this for any math operations.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Math expression to evaluate (e.g., '2 + 2', '10 * 5')"
                }
            },
            "required": ["expression"]
        }
    },
    {
        "name": "get_weather",
        "description": "Get the current weather for a location.",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City name (e.g., 'San Francisco')"
                }
            },
            "required": ["location"]
        }
    }
]


# =============================================================================
# COMPONENT 2: TOOL EXECUTION
# =============================================================================
# This function handles the actual execution of tools.
# In a real agent, these would connect to APIs, databases, etc.

def execute_tool(tool_name: str, tool_input: dict[str, Any]) -> str:
    """Execute a tool and return the result as a string."""

    if tool_name == "calculator":
        try:
            # Safe eval for basic math only
            allowed = {"__builtins__": {}}
            result = eval(tool_input["expression"], allowed)
            return f"Result: {result}"
        except Exception as e:
            return f"Error: {e}"

    elif tool_name == "get_weather":
        # Simulated weather response (in production, call a real API)
        location = tool_input["location"]
        return f"Weather in {location}: 72°F, Sunny with light clouds"

    return f"Unknown tool: {tool_name}"


# =============================================================================
# COMPONENT 3: THE AGENT CLASS
# =============================================================================

class SimpleAgent:
    """
    A minimal autonomous agent demonstrating the core concepts.

    The agent has:
    - A client to communicate with Claude (the LLM brain)
    - A list of tools it can use
    - Conversation memory to track the interaction
    """

    def __init__(self, api_key: str):
        # COMPONENT 3a: LLM BRAIN
        # The Anthropic client lets us communicate with Claude
        self.client = anthropic.Anthropic(api_key=api_key)

        # COMPONENT 3b: MEMORY
        # Conversation history maintains context across iterations
        self.messages: list[dict[str, Any]] = []

    def run(self, user_task: str, max_turns: int = 10) -> str:
        """
        Run the agent on a task.

        This is the AGENT LOOP - the heart of any autonomous agent.
        It follows the pattern: Observe -> Think -> Act -> Repeat
        """

        print(f"\n{'='*50}")
        print(f"Task: {user_task}")
        print(f"{'='*50}")

        # Start with the user's task
        self.messages = [{"role": "user", "content": user_task}]

        # =================================================================
        # COMPONENT 4: THE AGENT LOOP
        # =================================================================
        # This loop continues until:
        #   - The agent completes the task (stop_reason == "end_turn")
        #   - We hit max iterations (safety limit)

        for turn in range(max_turns):
            print(f"\n--- Turn {turn + 1} ---")

            # STEP 1: THINK
            # Send messages to Claude and get a response
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1024,
                tools=TOOLS,
                messages=self.messages
            )

            # STEP 2: CHECK IF DONE
            # If stop_reason is "end_turn", the agent has finished
            if response.stop_reason == "end_turn":
                # Extract the final text response
                for block in response.content:
                    if hasattr(block, "text"):
                        print(f"\nAgent: {block.text}")
                        return block.text
                return "Task completed."

            # STEP 3: ACT (if the agent wants to use tools)
            if response.stop_reason == "tool_use":
                # Add the assistant's response to memory
                self.messages.append({
                    "role": "assistant",
                    "content": response.content
                })

                # Execute each tool the agent requested
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        print(f"Using tool: {block.name}")
                        print(f"  Input: {json.dumps(block.input)}")

                        # Execute the tool
                        result = execute_tool(block.name, block.input)
                        print(f"  Result: {result}")

                        # Collect the result
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result
                        })

                # STEP 4: OBSERVE
                # Add tool results to memory so the agent can see them
                self.messages.append({
                    "role": "user",
                    "content": tool_results
                })

        return "Max turns reached."


# =============================================================================
# MAIN - RUNNING THE AGENT
# =============================================================================

def main():
    # Get API key from environment
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Please set ANTHROPIC_API_KEY environment variable")
        print("  export ANTHROPIC_API_KEY='your-key-here'")
        return

    # Create the agent
    agent = SimpleAgent(api_key)

    # Run with a sample task
    result = agent.run("What is 15% of 200? Also, what's the weather in Tokyo?")

    print(f"\n{'='*50}")
    print(f"Final Result: {result}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
