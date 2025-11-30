"""
Research Agent - finds restaurants, events, and places to visit.
"""

from typing import List, Dict, Any
import json
from datetime import datetime

from core.base_agent import BaseAgent
from core.types import AgentCapability, ToolDefinition


class ResearchAgent(BaseAgent):
    """
    Agent specialized in researching places to visit, events, and restaurants.

    Phase 1: Focuses on restaurant search
    Future: Will expand to events and attractions
    """

    def __init__(self, api_key: str, memory_store=None):
        """
        Initialize the Research Agent.

        Args:
            api_key: Anthropic API key
            memory_store: Optional memory store for saving recommendations
        """
        self.memory_store = memory_store
        super().__init__(name="research_agent", api_key=api_key)

    def _define_capabilities(self) -> List[AgentCapability]:
        """Define what this agent can do"""
        return [
            AgentCapability(
                name="find_restaurants",
                description="Search for restaurants by cuisine, location, and preferences",
                keywords=[
                    "restaurant", "food", "eat", "dining", "cuisine",
                    "lunch", "dinner", "breakfast", "cafe", "bistro",
                    "italian", "chinese", "japanese", "mexican", "thai",
                    "sushi", "pizza", "burger"
                ],
                required_inputs=["location"],
                optional_inputs=["cuisine", "price_range", "rating"],
                examples=[
                    "Find Italian restaurants in downtown",
                    "Where can I get sushi near Pike Place?",
                    "Best restaurants in Seattle"
                ]
            ),
            # Future capabilities:
            # AgentCapability(
            #     name="find_events",
            #     description="Search for events, concerts, shows",
            #     keywords=["event", "concert", "show", "festival"],
            #     ...
            # ),
        ]

    def _define_tools(self) -> List[ToolDefinition]:
        """Define tools this agent can use"""
        return [
            ToolDefinition(
                name="search_restaurants",
                description="Search for restaurants based on criteria like cuisine, location, price range",
                input_schema={
                    "type": "object",
                    "properties": {
                        "cuisine": {
                            "type": "string",
                            "description": "Type of cuisine (e.g., Italian, Chinese, Mexican)"
                        },
                        "location": {
                            "type": "string",
                            "description": "Location to search in (e.g., downtown Seattle, Pike Place)"
                        },
                        "price_range": {
                            "type": "string",
                            "description": "Price range: $ (cheap), $$ (moderate), $$$ (expensive), $$$$ (very expensive)"
                        },
                        "min_rating": {
                            "type": "number",
                            "description": "Minimum rating (1-5)"
                        },
                        "max_results": {
                            "type": "number",
                            "description": "Maximum number of results to return (default: 5)"
                        }
                    },
                    "required": []
                }
            ),
            ToolDefinition(
                name="get_restaurant_details",
                description="Get detailed information about a specific restaurant",
                input_schema={
                    "type": "object",
                    "properties": {
                        "restaurant_name": {
                            "type": "string",
                            "description": "Name of the restaurant"
                        },
                        "location": {
                            "type": "string",
                            "description": "Location/city of the restaurant"
                        }
                    },
                    "required": ["restaurant_name"]
                }
            ),
            ToolDefinition(
                name="save_recommendation",
                description="Save a restaurant recommendation to memory for future reference",
                input_schema={
                    "type": "object",
                    "properties": {
                        "restaurant": {
                            "type": "object",
                            "description": "Restaurant data to save"
                        }
                    },
                    "required": ["restaurant"]
                }
            )
        ]

    def _define_system_prompt(self) -> str:
        """Define the system prompt for this agent"""
        return """You are a research agent specialized in finding restaurants, events, and places to visit.

Your responsibilities:
1. Help users find restaurants based on their preferences
2. Provide detailed, accurate information
3. Consider user preferences like cuisine type, location, price range, and ratings
4. Save recommendations to memory for future reference

When searching:
- Use the search_restaurants tool to find options
- Use get_restaurant_details for specific information
- Save good recommendations using save_recommendation

Be thorough, accurate, and helpful. Present results in a clear, organized way."""

    def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """Execute a tool and return the result"""

        if tool_name == "search_restaurants":
            return self._search_restaurants(tool_input)

        elif tool_name == "get_restaurant_details":
            return self._get_restaurant_details(tool_input)

        elif tool_name == "save_recommendation":
            return self._save_recommendation(tool_input)

        else:
            return f"Unknown tool: {tool_name}"

    def _search_restaurants(self, params: Dict[str, Any]) -> str:
        """
        Search for restaurants.

        In production, this would call Google Maps API, Yelp API, etc.
        For now, we'll return mock data that demonstrates the functionality.

        Args:
            params: Search parameters

        Returns:
            JSON string with restaurant results
        """
        cuisine = params.get("cuisine", "")
        location = params.get("location", "")
        price_range = params.get("price_range", "$$")
        min_rating = params.get("min_rating", 3.5)
        max_results = params.get("max_results", 5)

        print(f"[Research Agent] Searching: cuisine={cuisine}, location={location}")

        # Mock data - in production, call real APIs
        mock_restaurants = self._get_mock_restaurants(cuisine, location, price_range, min_rating)

        # Limit results
        results = mock_restaurants[:max_results]

        return json.dumps({
            "restaurants": results,
            "count": len(results),
            "search_params": params
        }, indent=2)

    def _get_mock_restaurants(self, cuisine: str, location: str, price: str, min_rating: float) -> List[Dict]:
        """
        Generate mock restaurant data.

        In production, replace this with real API calls.
        """
        # Database of mock restaurants
        all_restaurants = [
            {
                "name": "Pasta Paradise",
                "cuisine": "Italian",
                "location": "Downtown Seattle",
                "rating": 4.5,
                "price_range": "$$",
                "highlights": ["Fresh pasta", "Wine selection", "Outdoor seating"],
                "address": "123 Main St, Seattle, WA",
                "phone": "(206) 555-0123"
            },
            {
                "name": "Trattoria Milano",
                "cuisine": "Italian",
                "location": "Capitol Hill",
                "rating": 4.7,
                "price_range": "$$$",
                "highlights": ["Authentic recipes", "Romantic atmosphere", "Great service"],
                "address": "456 Broadway Ave, Seattle, WA",
                "phone": "(206) 555-0456"
            },
            {
                "name": "Sushi Zen",
                "cuisine": "Japanese",
                "location": "Downtown Seattle",
                "rating": 4.6,
                "price_range": "$$$",
                "highlights": ["Fresh fish", "Omakase", "Sake selection"],
                "address": "789 Pike St, Seattle, WA",
                "phone": "(206) 555-0789"
            },
            {
                "name": "Taco Fiesta",
                "cuisine": "Mexican",
                "location": "Fremont",
                "rating": 4.3,
                "price_range": "$",
                "highlights": ["Authentic tacos", "Fresh ingredients", "Casual vibe"],
                "address": "321 Fremont Ave, Seattle, WA",
                "phone": "(206) 555-0321"
            },
            {
                "name": "The Golden Dragon",
                "cuisine": "Chinese",
                "location": "International District",
                "rating": 4.4,
                "price_range": "$$",
                "highlights": ["Dim sum", "Peking duck", "Family style"],
                "address": "654 Jackson St, Seattle, WA",
                "phone": "(206) 555-0654"
            },
            {
                "name": "Thai Basil",
                "cuisine": "Thai",
                "location": "University District",
                "rating": 4.2,
                "price_range": "$",
                "highlights": ["Pad Thai", "Curry", "Vegetarian options"],
                "address": "987 University Way, Seattle, WA",
                "phone": "(206) 555-0987"
            },
            {
                "name": "Le Petit Bistro",
                "cuisine": "French",
                "location": "Queen Anne",
                "rating": 4.8,
                "price_range": "$$$$",
                "highlights": ["Fine dining", "Tasting menu", "Wine pairings"],
                "address": "147 Queen Anne Ave, Seattle, WA",
                "phone": "(206) 555-0147"
            },
            {
                "name": "Burger Shack",
                "cuisine": "American",
                "location": "Ballard",
                "rating": 4.0,
                "price_range": "$",
                "highlights": ["Juicy burgers", "Craft beer", "Casual"],
                "address": "258 Ballard Ave, Seattle, WA",
                "phone": "(206) 555-0258"
            }
        ]

        # Filter by cuisine
        filtered = all_restaurants
        if cuisine:
            filtered = [r for r in filtered if cuisine.lower() in r["cuisine"].lower()]

        # Filter by location
        if location:
            filtered = [r for r in filtered if location.lower() in r["location"].lower()]

        # Filter by rating
        filtered = [r for r in filtered if r["rating"] >= min_rating]

        # Filter by price (if specified)
        if price and price != "$$":
            filtered = [r for r in filtered if r["price_range"] == price]

        # Sort by rating
        filtered.sort(key=lambda x: x["rating"], reverse=True)

        return filtered

    def _get_restaurant_details(self, params: Dict[str, Any]) -> str:
        """
        Get detailed information about a specific restaurant.

        Args:
            params: Must include 'restaurant_name'

        Returns:
            JSON string with restaurant details
        """
        restaurant_name = params.get("restaurant_name")
        location = params.get("location", "")

        print(f"[Research Agent] Getting details for: {restaurant_name}")

        # In production, call real API
        # For now, search mock data
        all_restaurants = self._get_mock_restaurants("", "", "$$", 0)

        for restaurant in all_restaurants:
            if restaurant_name.lower() in restaurant["name"].lower():
                # Add additional details
                details = {
                    **restaurant,
                    "hours": "Mon-Thu: 11am-10pm, Fri-Sat: 11am-11pm, Sun: 12pm-9pm",
                    "accepts_reservations": True,
                    "popular_dishes": ["Dish 1", "Dish 2", "Dish 3"],
                    "reviews_summary": "Customers love the food quality and service."
                }
                return json.dumps(details, indent=2)

        return json.dumps({
            "error": f"Restaurant '{restaurant_name}' not found"
        })

    def _save_recommendation(self, params: Dict[str, Any]) -> str:
        """
        Save a restaurant recommendation to memory.

        Args:
            params: Must include 'restaurant' dict

        Returns:
            Success message
        """
        restaurant = params.get("restaurant", {})

        if not restaurant:
            return "Error: No restaurant data provided"

        # Save to memory store if available
        if self.memory_store:
            try:
                self.memory_store.save_recommendation(
                    type="restaurant",
                    data=restaurant
                )
                return f"Saved recommendation: {restaurant.get('name', 'Unknown')}"
            except Exception as e:
                return f"Error saving to memory: {str(e)}"
        else:
            # Just acknowledge without saving
            return f"Acknowledged recommendation: {restaurant.get('name', 'Unknown')} (memory not configured)"
