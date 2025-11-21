"""
Simple Autonomous Agent Example
================================
A minimal implementation of an autonomous AI agent using Claude.
"""

import anthropic
import json
import os
from typing import List, Dict, Any


class SimpleAutonomousAgent:
    """
    A simple autonomous agent that can use tools to complete tasks.

    This agent demonstrates the core loop:
    1. Receive a task from the user
    2. Reason about what tools to use
    3. Execute tools
    4. Reflect on results
    5. Continue until task is complete
    """

    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.conversation_history: List[Dict[str, Any]] = []
        self.tools = self._define_tools()

    def _define_tools(self) -> List[Dict[str, Any]]:
        """Define the tools available to the agent"""
        return [
            {
                "name": "read_file",
                "description": "Read the contents of a file from the filesystem",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "filepath": {
                            "type": "string",
                            "description": "The path to the file to read"
                        }
                    },
                    "required": ["filepath"]
                }
            },
            {
                "name": "write_file",
                "description": "Write content to a file on the filesystem",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "filepath": {
                            "type": "string",
                            "description": "The path to the file to write"
                        },
                        "content": {
                            "type": "string",
                            "description": "The content to write to the file"
                        }
                    },
                    "required": ["filepath", "content"]
                }
            },
            {
                "name": "list_files",
                "description": "List all files in a directory",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "directory": {
                            "type": "string",
                            "description": "The directory path to list files from"
                        }
                    },
                    "required": ["directory"]
                }
            },
            {
                "name": "calculate",
                "description": "Perform mathematical calculations",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "The mathematical expression to evaluate"
                        }
                    },
                    "required": ["expression"]
                }
            }
        ]

    def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """Execute a tool and return the result"""
        try:
            if tool_name == "read_file":
                with open(tool_input["filepath"], 'r') as f:
                    content = f.read()
                return f"File content:\n{content}"

            elif tool_name == "write_file":
                with open(tool_input["filepath"], 'w') as f:
                    f.write(tool_input["content"])
                return f"Successfully wrote to {tool_input['filepath']}"

            elif tool_name == "list_files":
                directory = tool_input["directory"]
                files = os.listdir(directory)
                return f"Files in {directory}:\n" + "\n".join(files)

            elif tool_name == "calculate":
                # Safe evaluation for basic math
                result = eval(tool_input["expression"], {"__builtins__": {}}, {})
                return f"Result: {result}"

            else:
                return f"Error: Unknown tool '{tool_name}'"

        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"

    def run(self, task: str, max_iterations: int = 10) -> str:
        """
        Run the agent on a task.

        Args:
            task: The task description from the user
            max_iterations: Maximum number of agent reasoning loops

        Returns:
            The final response from the agent
        """
        print(f"\n{'='*60}")
        print(f"AGENT STARTING TASK")
        print(f"{'='*60}")
        print(f"Task: {task}\n")

        # Initialize conversation with the task
        self.conversation_history = [{
            "role": "user",
            "content": task
        }]

        iteration = 0
        while iteration < max_iterations:
            iteration += 1
            print(f"\n--- Iteration {iteration} ---")

            # Get response from Claude
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4096,
                tools=self.tools,
                messages=self.conversation_history
            )

            # Print reasoning
            for block in response.content:
                if hasattr(block, "text"):
                    print(f"\nAgent Thinking: {block.text}")

            # Check if agent is done
            if response.stop_reason == "end_turn":
                print(f"\n{'='*60}")
                print("AGENT COMPLETED TASK")
                print(f"{'='*60}\n")

                # Extract final text response
                final_response = next(
                    (block.text for block in response.content
                     if hasattr(block, "text")),
                    "Task completed"
                )
                return final_response

            # Agent wants to use tools
            elif response.stop_reason == "tool_use":
                # Add assistant response to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response.content
                })

                # Execute all requested tools
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        print(f"\nTool Use: {block.name}")
                        print(f"Input: {json.dumps(block.input, indent=2)}")

                        # Execute the tool
                        result = self._execute_tool(block.name, block.input)
                        print(f"Result: {result}")

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

        return "Task exceeded maximum iterations"


def main():
    """Example usage of the Simple Autonomous Agent"""

    # Get API key from environment
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: Please set ANTHROPIC_API_KEY environment variable")
        return

    # Create the agent
    agent = SimpleAutonomousAgent(api_key=api_key)

    # Example tasks
    tasks = [
        "Create a file called 'hello.txt' with the content 'Hello, World!'",
        "Calculate 15% of 240 and write the result to a file called 'result.txt'",
        "List all files in the current directory",
    ]

    # Run a task
    task = tasks[0]  # Change index to try different tasks
    result = agent.run(task)

    print(f"\nFinal Result: {result}")


if __name__ == "__main__":
    main()
