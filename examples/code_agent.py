"""
Code Development Agent Example
===============================
An autonomous agent that can write, test, and debug code.
"""

import anthropic
import os
import subprocess
from typing import List, Dict, Any


class CodeAgent:
    """
    An agent specialized in software development tasks.

    Capabilities:
    - Write code based on specifications
    - Run and test code
    - Debug errors
    - Refactor and improve code
    - Generate documentation
    """

    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.project_files: Dict[str, str] = {}

    def _get_tools(self) -> List[Dict[str, Any]]:
        """Define code development tools"""
        return [
            {
                "name": "write_code",
                "description": "Write code to a file",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "filename": {"type": "string"},
                        "code": {"type": "string"},
                        "language": {"type": "string"}
                    },
                    "required": ["filename", "code", "language"]
                }
            },
            {
                "name": "run_code",
                "description": "Execute code and return output",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "filename": {"type": "string"}
                    },
                    "required": ["filename"]
                }
            },
            {
                "name": "run_tests",
                "description": "Run tests for the code",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "test_file": {"type": "string"}
                    },
                    "required": ["test_file"]
                }
            },
            {
                "name": "read_code",
                "description": "Read existing code from a file",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "filename": {"type": "string"}
                    },
                    "required": ["filename"]
                }
            },
            {
                "name": "analyze_error",
                "description": "Analyze an error or stack trace",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "error": {"type": "string"}
                    },
                    "required": ["error"]
                }
            }
        ]

    def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """Execute code development tools"""
        try:
            if tool_name == "write_code":
                filename = tool_input["filename"]
                code = tool_input["code"]

                with open(filename, 'w') as f:
                    f.write(code)

                self.project_files[filename] = code
                return f"✅ Code written to {filename} ({len(code)} characters)"

            elif tool_name == "run_code":
                filename = tool_input["filename"]

                # Determine how to run the file
                if filename.endswith(".py"):
                    result = subprocess.run(
                        ["python", filename],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                elif filename.endswith(".js"):
                    result = subprocess.run(
                        ["node", filename],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                else:
                    return "❌ Unsupported file type"

                output = result.stdout if result.returncode == 0 else result.stderr
                status = "✅ Success" if result.returncode == 0 else "❌ Error"

                return f"{status}\n\nOutput:\n{output}"

            elif tool_name == "run_tests":
                test_file = tool_input["test_file"]

                result = subprocess.run(
                    ["python", "-m", "pytest", test_file, "-v"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                return f"Test Results:\n{result.stdout}\n{result.stderr}"

            elif tool_name == "read_code":
                filename = tool_input["filename"]

                if filename in self.project_files:
                    return self.project_files[filename]

                try:
                    with open(filename, 'r') as f:
                        return f.read()
                except FileNotFoundError:
                    return f"❌ File not found: {filename}"

            elif tool_name == "analyze_error":
                error = tool_input["error"]
                return f"Analyzing error:\n{error}\n\nSuggestions will be provided in next iteration."

            return f"Unknown tool: {tool_name}"

        except subprocess.TimeoutExpired:
            return "❌ Execution timed out"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def develop(self, specification: str) -> str:
        """
        Develop code based on a specification.

        The agent will:
        1. Understand the requirements
        2. Write the code
        3. Test it
        4. Fix any issues
        5. Deliver working code
        """
        system_prompt = """You are an expert software development agent.

Your workflow:
1. Analyze the specification carefully
2. Break down into components
3. Write clean, well-documented code
4. Test your code thoroughly
5. Debug and fix any errors
6. Iterate until the code works correctly

Always write production-quality code with:
- Clear variable names
- Proper error handling
- Comments explaining complex logic
- Type hints (for Python)

When you encounter errors, analyze them carefully and fix them systematically."""

        messages = [
            {
                "role": "user",
                "content": f"Develop the following:\n\n{specification}"
            }
        ]

        print(f"\n👨‍💻 Starting development...")
        print(f"📋 Specification: {specification}\n")

        max_iterations = 20
        for i in range(max_iterations):
            print(f"\n--- Iteration {i+1} ---")

            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4096,
                system=system_prompt,
                tools=self._get_tools(),
                messages=messages
            )

            # Show agent thinking
            for block in response.content:
                if hasattr(block, "text") and block.text:
                    print(f"\n💭 Agent: {block.text}")

            if response.stop_reason == "end_turn":
                final_response = next(
                    (block.text for block in response.content
                     if hasattr(block, "text")),
                    "Development completed"
                )
                print(f"\n{'='*60}")
                print("✅ DEVELOPMENT COMPLETE")
                print(f"{'='*60}")
                return final_response

            # Execute tools
            messages.append({
                "role": "assistant",
                "content": response.content
            })

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"\n🔧 Tool: {block.name}")
                    result = self._execute_tool(block.name, block.input)
                    print(f"Result: {result}")

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })

            messages.append({
                "role": "user",
                "content": tool_results
            })

        return "Development session ended (max iterations)"


def main():
    """Example usage"""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Please set ANTHROPIC_API_KEY environment variable")
        return

    agent = CodeAgent(api_key=api_key)

    # Example development tasks
    specifications = [
        """
        Create a Python function that:
        - Takes a list of numbers
        - Returns the median value
        - Handles edge cases (empty list, single element)
        - Includes error handling
        - Has comprehensive docstrings

        Then write tests to verify it works correctly.
        """,

        """
        Create a simple task manager CLI in Python that:
        - Adds tasks
        - Lists all tasks
        - Marks tasks as complete
        - Saves tasks to a JSON file
        """,
    ]

    result = agent.develop(specifications[0])
    print(f"\nFinal Result:\n{result}")

    # Show created files
    print(f"\n📁 Files created:")
    for filename in agent.project_files.keys():
        print(f"  - {filename}")


if __name__ == "__main__":
    main()
