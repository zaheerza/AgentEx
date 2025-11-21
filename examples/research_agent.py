"""
Research Agent Example
======================
An autonomous agent that can research topics and compile reports.
"""

import anthropic
import os
from typing import List, Dict, Any
import json


class ResearchAgent:
    """
    An agent specialized in researching topics and creating reports.

    This agent demonstrates:
    - Breaking down complex research tasks
    - Using multiple information sources
    - Synthesizing information
    - Creating structured outputs
    """

    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.research_notes: List[str] = []

    def _get_tools(self) -> List[Dict[str, Any]]:
        """Define research-specific tools"""
        return [
            {
                "name": "web_search",
                "description": "Search the web for information on a topic",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "save_note",
                "description": "Save an important finding or note",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "note": {
                            "type": "string",
                            "description": "The note or finding to save"
                        },
                        "category": {
                            "type": "string",
                            "description": "Category for the note (e.g., 'definition', 'example', 'statistic')"
                        }
                    },
                    "required": ["note", "category"]
                }
            },
            {
                "name": "create_report",
                "description": "Create a structured research report",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "sections": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "heading": {"type": "string"},
                                    "content": {"type": "string"}
                                }
                            }
                        }
                    },
                    "required": ["title", "sections"]
                }
            }
        ]

    def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """Execute research tools"""
        if tool_name == "web_search":
            # In a real implementation, this would call a search API
            query = tool_input["query"]
            # Simulated search results
            mock_results = f"""
Search results for: {query}

1. {query} is a fundamental concept in computer science and AI.
2. Recent developments in {query} have shown promising results.
3. Key applications include automation, decision-making, and data analysis.
4. Challenges include scalability, reliability, and ethical considerations.
"""
            return mock_results

        elif tool_name == "save_note":
            note = f"[{tool_input['category']}] {tool_input['note']}"
            self.research_notes.append(note)
            return f"Note saved: {note}"

        elif tool_name == "create_report":
            title = tool_input["title"]
            report = f"# {title}\n\n"

            for section in tool_input["sections"]:
                report += f"## {section['heading']}\n\n"
                report += f"{section['content']}\n\n"

            # Add research notes
            if self.research_notes:
                report += "## Research Notes\n\n"
                for note in self.research_notes:
                    report += f"- {note}\n"

            # Save to file
            filename = title.lower().replace(" ", "_") + ".md"
            with open(filename, 'w') as f:
                f.write(report)

            return f"Report created and saved to {filename}"

        return f"Unknown tool: {tool_name}"

    def research(self, topic: str, depth: str = "comprehensive") -> str:
        """
        Research a topic and create a report.

        Args:
            topic: The topic to research
            depth: Level of detail ('quick', 'standard', 'comprehensive')
        """
        system_prompt = f"""You are a research agent. Your task is to:

1. Research the given topic thoroughly
2. Use web_search to gather information
3. Use save_note to record important findings
4. Synthesize the information
5. Create a well-structured report using create_report

Research depth: {depth}

Be thorough, cite key findings, and organize information logically."""

        messages = [
            {
                "role": "user",
                "content": f"Research this topic and create a comprehensive report: {topic}"
            }
        ]

        print(f"\n🔍 Researching: {topic}")
        print(f"📊 Depth: {depth}\n")

        max_iterations = 15
        for i in range(max_iterations):
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4096,
                system=system_prompt,
                tools=self._get_tools(),
                messages=messages
            )

            # Show thinking
            for block in response.content:
                if hasattr(block, "text") and block.text:
                    print(f"💭 {block.text}\n")

            if response.stop_reason == "end_turn":
                final_response = next(
                    (block.text for block in response.content
                     if hasattr(block, "text")),
                    "Research completed"
                )
                return final_response

            # Execute tools
            messages.append({
                "role": "assistant",
                "content": response.content
            })

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"🔧 Using tool: {block.name}")
                    result = self._execute_tool(block.name, block.input)
                    print(f"✅ {result}\n")

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })

            messages.append({
                "role": "user",
                "content": tool_results
            })

        return "Research completed (max iterations reached)"


def main():
    """Example usage"""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Please set ANTHROPIC_API_KEY environment variable")
        return

    agent = ResearchAgent(api_key=api_key)

    # Research topics
    topics = [
        "Autonomous AI Agents",
        "Reinforcement Learning",
        "Vector Databases",
    ]

    result = agent.research(topics[0], depth="comprehensive")
    print(f"\n{'='*60}")
    print(f"RESEARCH COMPLETE")
    print(f"{'='*60}")
    print(f"\n{result}")


if __name__ == "__main__":
    main()
