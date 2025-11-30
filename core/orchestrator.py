"""
Orchestrator Agent - coordinates all sub-agents and manages user interactions.
"""

from typing import List, Dict, Any, Optional
import anthropic
from datetime import datetime

from .types import Task, AgentResult, Intent, ConversationMessage
from .base_agent import BaseAgent


class AgentRegistry:
    """Registry of available agents"""

    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent):
        """Register a new agent"""
        self.agents[agent.name] = agent
        print(f"[Registry] Registered agent: {agent.name}")

    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Get an agent by name"""
        return self.agents.get(name)

    def find_best_agent(self, query: str) -> Optional[BaseAgent]:
        """
        Find the best agent to handle a query.

        Args:
            query: User query string

        Returns:
            Best matching agent or None
        """
        best_agent = None
        best_score = 0.0

        for agent in self.agents.values():
            score = agent.can_handle(query)
            print(f"[Registry] {agent.name} confidence: {score:.2f}")

            if score > best_score:
                best_score = score
                best_agent = agent

        if best_score > 0.3:  # Minimum confidence threshold
            return best_agent

        return None

    def list_agents(self) -> List[str]:
        """List all registered agent names"""
        return list(self.agents.keys())


class OrchestratorAgent:
    """
    Main orchestrator that coordinates all sub-agents.

    The orchestrator:
    - Receives user input
    - Analyzes intent
    - Routes to appropriate agent(s)
    - Manages conversation context
    - Aggregates and presents results
    """

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5-20250929"):
        """
        Initialize the orchestrator.

        Args:
            api_key: Anthropic API key
            model: Claude model to use for intent recognition
        """
        self.api_key = api_key
        self.model = model
        self.client = anthropic.Anthropic(api_key=api_key)

        # Agent management
        self.registry = AgentRegistry()

        # Conversation state
        self.conversation_history: List[ConversationMessage] = []
        self.session_context: Dict[str, Any] = {
            "user_preferences": {},
            "current_session_id": datetime.now().isoformat()
        }

    def register_agent(self, agent: BaseAgent):
        """
        Register a new agent with the orchestrator.

        Args:
            agent: Agent instance to register
        """
        self.registry.register(agent)

    def handle_input(self, user_input: str) -> str:
        """
        Main entry point for user interaction.

        Args:
            user_input: User's message/query

        Returns:
            Response string to display to user
        """
        print(f"\n{'='*60}")
        print(f"[Orchestrator] Received: {user_input}")
        print(f"{'='*60}")

        # Add to conversation history
        self.conversation_history.append(
            ConversationMessage(role="user", content=user_input)
        )

        try:
            # Step 1: Analyze intent and find appropriate agent
            agent = self._route_to_agent(user_input)

            if not agent:
                response = self._handle_unknown_intent(user_input)
            else:
                # Step 2: Create task for the agent
                task = self._create_task(user_input, agent)

                # Step 3: Execute task
                result = agent.execute(task)

                # Step 4: Format and return response
                response = self._format_response(result)

            # Add assistant response to history
            self.conversation_history.append(
                ConversationMessage(role="assistant", content=response)
            )

            return response

        except Exception as e:
            error_msg = f"I encountered an error: {str(e)}"
            print(f"[Orchestrator] Error: {str(e)}")
            return error_msg

    def _route_to_agent(self, user_input: str) -> Optional[BaseAgent]:
        """
        Determine which agent should handle the user input.

        Args:
            user_input: User's query

        Returns:
            Best matching agent or None
        """
        print(f"\n[Orchestrator] Routing query...")

        # Find best matching agent
        agent = self.registry.find_best_agent(user_input)

        if agent:
            print(f"[Orchestrator] Routing to: {agent.name}")
        else:
            print(f"[Orchestrator] No suitable agent found")

        return agent

    def _create_task(self, user_input: str, agent: BaseAgent) -> Task:
        """
        Create a task for the agent to execute.

        Args:
            user_input: User's query
            agent: Agent that will execute the task

        Returns:
            Task object
        """
        # Extract parameters from user input using simple keyword extraction
        parameters = self._extract_parameters(user_input)

        task = Task(
            description=user_input,
            parameters=parameters,
            context={
                "user_preferences": self.session_context.get("user_preferences", {}),
                "session_id": self.session_context.get("current_session_id"),
                "conversation_history": self._get_recent_history(limit=5)
            }
        )

        return task

    def _extract_parameters(self, user_input: str) -> Dict[str, Any]:
        """
        Extract parameters from user input.

        This is a simple implementation. In production, you might use
        more sophisticated NER (Named Entity Recognition).

        Args:
            user_input: User's query

        Returns:
            Dictionary of extracted parameters
        """
        parameters = {}
        user_input_lower = user_input.lower()

        # Extract cuisine type
        cuisines = ["italian", "chinese", "japanese", "indian", "mexican",
                   "thai", "french", "american", "korean", "vietnamese",
                   "sushi", "pizza", "burger"]
        for cuisine in cuisines:
            if cuisine in user_input_lower:
                parameters["cuisine"] = cuisine.capitalize()
                break

        # Extract location keywords
        location_keywords = ["downtown", "in", "near", "around"]
        for keyword in location_keywords:
            if keyword in user_input_lower:
                # Simple extraction - in production use better NER
                words = user_input.split()
                try:
                    idx = [w.lower() for w in words].index(keyword)
                    if idx + 1 < len(words):
                        location_parts = []
                        for i in range(idx + 1, min(idx + 3, len(words))):
                            location_parts.append(words[i])
                        parameters["location"] = " ".join(location_parts).strip(".,!?")
                        break
                except ValueError:
                    pass

        # Extract price indicators
        if any(word in user_input_lower for word in ["cheap", "budget", "affordable"]):
            parameters["price_range"] = "$"
        elif any(word in user_input_lower for word in ["expensive", "upscale", "fancy"]):
            parameters["price_range"] = "$$$$"
        elif "$$" in user_input:
            parameters["price_range"] = "$$"

        # Extract rating preference
        if "highly rated" in user_input_lower or "best" in user_input_lower:
            parameters["min_rating"] = 4.0

        return parameters

    def _get_recent_history(self, limit: int = 5) -> List[Dict[str, str]]:
        """
        Get recent conversation history.

        Args:
            limit: Maximum number of messages to return

        Returns:
            List of recent messages
        """
        recent = self.conversation_history[-limit:]
        return [
            {"role": msg.role, "content": str(msg.content)}
            for msg in recent
        ]

    def _format_response(self, result: AgentResult) -> str:
        """
        Format agent result into user-friendly response.

        Args:
            result: Result from agent execution

        Returns:
            Formatted response string
        """
        if not result.success:
            return f"Sorry, I encountered an error: {result.error}"

        # Format based on result type
        if isinstance(result.data, dict):
            return self._format_structured_response(result.data)
        elif isinstance(result.data, str):
            return result.data
        else:
            return str(result.data)

    def _format_structured_response(self, data: Dict[str, Any]) -> str:
        """
        Format structured data (like restaurant results) into readable text.

        Args:
            data: Structured data dictionary

        Returns:
            Formatted string
        """
        # Check if it's restaurant data
        if "restaurants" in data:
            return self._format_restaurant_results(data["restaurants"])

        # Check if it's event data
        if "events" in data:
            return self._format_event_results(data["events"])

        # Default formatting
        return str(data)

    def _format_restaurant_results(self, restaurants: List[Dict[str, Any]]) -> str:
        """Format restaurant results"""
        if not restaurants:
            return "I couldn't find any restaurants matching your criteria."

        response = f"I found {len(restaurants)} restaurant(s):\n\n"

        for i, restaurant in enumerate(restaurants, 1):
            response += f"{i}. **{restaurant.get('name', 'Unknown')}**\n"

            if "cuisine" in restaurant:
                response += f"   - Cuisine: {restaurant['cuisine']}\n"

            if "rating" in restaurant:
                response += f"   - Rating: {restaurant['rating']}/5.0\n"

            if "price_range" in restaurant:
                response += f"   - Price: {restaurant['price_range']}\n"

            if "location" in restaurant:
                response += f"   - Location: {restaurant['location']}\n"

            if "highlights" in restaurant and restaurant['highlights']:
                response += f"   - Highlights: {', '.join(restaurant['highlights'])}\n"

            response += "\n"

        return response.strip()

    def _format_event_results(self, events: List[Dict[str, Any]]) -> str:
        """Format event results"""
        if not events:
            return "I couldn't find any events matching your criteria."

        response = f"I found {len(events)} event(s):\n\n"

        for i, event in enumerate(events, 1):
            response += f"{i}. **{event.get('name', 'Unknown')}**\n"

            if "date" in event:
                response += f"   - Date: {event['date']}\n"

            if "location" in event:
                response += f"   - Location: {event['location']}\n"

            if "description" in event:
                response += f"   - Description: {event['description']}\n"

            response += "\n"

        return response.strip()

    def _handle_unknown_intent(self, user_input: str) -> str:
        """
        Handle queries that don't match any agent.

        Uses Claude directly to provide a helpful response.

        Args:
            user_input: User's query

        Returns:
            Response string
        """
        print("[Orchestrator] No matching agent, using general response")

        # List available capabilities
        capabilities_text = self._list_capabilities()

        prompt = f"""I don't have a specialized agent to handle this request: "{user_input}"

Here's what I can help you with:

{capabilities_text}

Please rephrase your request or ask me something I can help with."""

        return prompt

    def _list_capabilities(self) -> str:
        """List all available agent capabilities"""
        capabilities = []

        for agent_name in self.registry.list_agents():
            agent = self.registry.get_agent(agent_name)
            if agent:
                capabilities.append(f"\n**{agent_name}:**")
                for cap in agent.capabilities:
                    capabilities.append(f"  - {cap.description}")
                    if cap.examples:
                        capabilities.append(f"    Examples: {', '.join(cap.examples[:2])}")

        return "\n".join(capabilities) if capabilities else "No agents registered yet."

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        print("[Orchestrator] Conversation history cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics"""
        return {
            "registered_agents": self.registry.list_agents(),
            "conversation_length": len(self.conversation_history),
            "session_id": self.session_context.get("current_session_id")
        }
