"""
Base agent class that all task-specific agents inherit from.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import anthropic
from datetime import datetime

from .types import (
    AgentCapability,
    Task,
    AgentResult,
    ToolDefinition,
    ConversationMessage
)


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the system.

    All task-specific agents (Research, Feedback, Deals, Writing)
    inherit from this class and implement the abstract methods.
    """

    def __init__(self, name: str, api_key: str, model: str = "claude-sonnet-4-5-20250929"):
        """
        Initialize the agent.

        Args:
            name: Unique name for this agent
            api_key: Anthropic API key
            model: Claude model to use
        """
        self.name = name
        self.model = model
        self.client = anthropic.Anthropic(api_key=api_key)

        # Agent configuration
        self.capabilities = self._define_capabilities()
        self.tools = self._define_tools()
        self.system_prompt = self._define_system_prompt()

        # Execution state
        self._iteration_count = 0
        self._max_iterations = 15
        self.conversation_history: List[Dict[str, Any]] = []

    @abstractmethod
    def _define_capabilities(self) -> List[AgentCapability]:
        """
        Define what this agent can do.

        Returns:
            List of capabilities this agent supports
        """
        pass

    @abstractmethod
    def _define_tools(self) -> List[ToolDefinition]:
        """
        Define tools this agent can use.

        Returns:
            List of tool definitions
        """
        pass

    @abstractmethod
    def _define_system_prompt(self) -> str:
        """
        Define the system prompt for this agent.

        Returns:
            System prompt string
        """
        pass

    @abstractmethod
    def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """
        Execute a tool and return the result.

        Args:
            tool_name: Name of the tool to execute
            tool_input: Input parameters for the tool

        Returns:
            Result string from tool execution
        """
        pass

    def can_handle(self, intent_query: str) -> float:
        """
        Determine if this agent can handle a given query.

        Args:
            intent_query: The user's query string

        Returns:
            Confidence score (0-1) that this agent can handle the query
        """
        max_score = 0.0

        for capability in self.capabilities:
            score = capability.matches_intent(intent_query)
            max_score = max(max_score, score)

        return max_score

    def execute(self, task: Task) -> AgentResult:
        """
        Main execution method called by orchestrator.

        Args:
            task: The task to execute

        Returns:
            AgentResult with execution outcome
        """
        print(f"\n[{self.name}] Starting task: {task.task_id}")
        print(f"[{self.name}] Description: {task.description}")

        try:
            result_data = self._run_agent_loop(task)

            return AgentResult(
                task_id=task.task_id,
                agent_name=self.name,
                success=True,
                data=result_data,
                metadata={
                    "iterations": self._iteration_count,
                    "model": self.model
                }
            )
        except Exception as e:
            print(f"[{self.name}] Error: {str(e)}")
            return AgentResult(
                task_id=task.task_id,
                agent_name=self.name,
                success=False,
                data=None,
                metadata={"iterations": self._iteration_count},
                error=str(e)
            )

    def _run_agent_loop(self, task: Task) -> Any:
        """
        Internal agent execution loop using ReAct pattern.

        This implements the core observe-think-act cycle:
        1. Agent thinks about the task
        2. Decides which tool to use
        3. Executes the tool
        4. Observes the result
        5. Repeats until task is complete

        Args:
            task: The task to execute

        Returns:
            The final result data
        """
        # Initialize conversation with the task
        self.conversation_history = [
            {
                "role": "user",
                "content": self._format_task_prompt(task)
            }
        ]

        self._iteration_count = 0

        # Convert tools to Anthropic format
        anthropic_tools = [tool.to_anthropic_format() for tool in self.tools]

        while self._iteration_count < self._max_iterations:
            self._iteration_count += 1
            print(f"\n[{self.name}] Iteration {self._iteration_count}/{self._max_iterations}")

            # Get response from Claude
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=self.system_prompt,
                tools=anthropic_tools,
                messages=self.conversation_history
            )

            # Log agent thinking
            for block in response.content:
                if hasattr(block, "text") and block.text:
                    print(f"[{self.name}] Thinking: {block.text[:200]}...")

            # Check stop reason
            if response.stop_reason == "end_turn":
                # Agent is done
                final_response = self._extract_final_response(response)
                print(f"[{self.name}] Task complete!")
                return final_response

            elif response.stop_reason == "tool_use":
                # Agent wants to use tools
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response.content
                })

                # Execute all requested tools
                tool_results = []
                for block in response.content:
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

        # Max iterations reached
        print(f"[{self.name}] Warning: Max iterations reached")
        return self._extract_partial_response()

    def _format_task_prompt(self, task: Task) -> str:
        """
        Format the task into a prompt for the agent.

        Args:
            task: The task to format

        Returns:
            Formatted prompt string
        """
        prompt = f"Task: {task.description}\n\n"

        if task.parameters:
            prompt += "Parameters:\n"
            for key, value in task.parameters.items():
                prompt += f"  - {key}: {value}\n"

        if task.context:
            prompt += "\nContext:\n"
            for key, value in task.context.items():
                if key == "user_preferences":
                    prompt += f"  - User preferences: {value}\n"
                elif key == "conversation_history":
                    # Don't include full history, just mention it exists
                    prompt += f"  - Conversation history available\n"
                else:
                    prompt += f"  - {key}: {value}\n"

        return prompt

    def _extract_final_response(self, response) -> Any:
        """
        Extract the final response from Claude's output.

        Args:
            response: The response from Claude API

        Returns:
            Extracted response data
        """
        # Try to find text content
        for block in response.content:
            if hasattr(block, "text"):
                return block.text

        return "Task completed"

    def _extract_partial_response(self) -> Any:
        """
        Extract partial response when max iterations reached.

        Returns:
            Best available response
        """
        # Look through conversation history for last meaningful response
        for msg in reversed(self.conversation_history):
            if msg["role"] == "assistant":
                content = msg["content"]
                if isinstance(content, list):
                    for block in content:
                        if hasattr(block, "text") and block.text:
                            return f"Partial result: {block.text}"
                elif isinstance(content, str):
                    return f"Partial result: {content}"

        return "Task incomplete (max iterations reached)"

    def reset_conversation(self):
        """Reset the conversation history."""
        self.conversation_history = []
        self._iteration_count = 0
