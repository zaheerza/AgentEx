"""
SQL-based memory store using SQLite.
"""

import sqlite3
import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path


class SQLMemoryStore:
    """
    SQLite-based memory store for the multi-agent system.

    Stores recommendations, feedback, preferences, and execution history.
    """

    def __init__(self, db_path: str = "data/memory.db"):
        """
        Initialize the memory store.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path

        # Create data directory if it doesn't exist
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._init_database()

    def _init_database(self):
        """Initialize the database with schema"""
        # Read schema file
        schema_path = Path(__file__).parent / "schemas.sql"

        with sqlite3.connect(self.db_path) as conn:
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            conn.executescript(schema_sql)
            conn.commit()

        print(f"[Memory] Database initialized at {self.db_path}")

    def save_recommendation(self, type: str, data: Dict[str, Any]) -> str:
        """
        Save a recommendation (restaurant, event, or place).

        Args:
            type: Type of recommendation ('restaurant', 'event', 'place')
            data: Recommendation data

        Returns:
            ID of saved recommendation
        """
        rec_id = str(uuid.uuid4())
        name = data.get("name", "Unknown")
        location = data.get("location", "")
        source_agent = data.get("source_agent", "unknown")

        # Store all data as JSON in metadata field
        metadata = json.dumps(data)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO recommendations (id, type, name, location, metadata, source_agent)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (rec_id, type, name, location, metadata, source_agent))
            conn.commit()

        print(f"[Memory] Saved {type}: {name} (ID: {rec_id})")
        return rec_id

    def get_recommendations(
        self,
        type: Optional[str] = None,
        visited: Optional[bool] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieve recommendations.

        Args:
            type: Filter by type (restaurant, event, place)
            visited: Filter by visited status
            limit: Maximum number of results

        Returns:
            List of recommendations
        """
        query = "SELECT * FROM recommendations WHERE 1=1"
        params = []

        if type:
            query += " AND type = ?"
            params.append(type)

        if visited is not None:
            query += " AND visited = ?"
            params.append(visited)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()

        results = []
        for row in rows:
            rec = {
                "id": row["id"],
                "type": row["type"],
                "name": row["name"],
                "location": row["location"],
                "visited": bool(row["visited"]),
                "created_at": row["created_at"],
                **json.loads(row["metadata"])
            }
            results.append(rec)

        return results

    def mark_visited(self, recommendation_id: str):
        """
        Mark a recommendation as visited.

        Args:
            recommendation_id: ID of the recommendation
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE recommendations
                SET visited = TRUE
                WHERE id = ?
            """, (recommendation_id,))
            conn.commit()

        print(f"[Memory] Marked recommendation {recommendation_id} as visited")

    def save_feedback(
        self,
        recommendation_id: str,
        rating: int,
        notes: str = "",
        liked: List[str] = None,
        disliked: List[str] = None,
        would_return: bool = True
    ) -> str:
        """
        Save feedback for a recommendation.

        Args:
            recommendation_id: ID of the recommendation
            rating: Rating 1-5
            notes: Free-form notes
            liked: List of things user liked
            disliked: List of things user disliked
            would_return: Whether user would return

        Returns:
            Feedback ID
        """
        feedback_id = str(uuid.uuid4())
        liked_json = json.dumps(liked or [])
        disliked_json = json.dumps(disliked or [])

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO feedback (id, recommendation_id, rating, notes, liked, disliked, would_return)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (feedback_id, recommendation_id, rating, notes, liked_json, disliked_json, would_return))
            conn.commit()

        # Mark recommendation as visited
        self.mark_visited(recommendation_id)

        print(f"[Memory] Saved feedback (ID: {feedback_id})")
        return feedback_id

    def get_feedback(self, recommendation_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve feedback.

        Args:
            recommendation_id: Optional filter by recommendation

        Returns:
            List of feedback entries
        """
        query = "SELECT * FROM feedback WHERE 1=1"
        params = []

        if recommendation_id:
            query += " AND recommendation_id = ?"
            params.append(recommendation_id)

        query += " ORDER BY created_at DESC"

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()

        results = []
        for row in rows:
            feedback = {
                "id": row["id"],
                "recommendation_id": row["recommendation_id"],
                "rating": row["rating"],
                "notes": row["notes"],
                "liked": json.loads(row["liked"]),
                "disliked": json.loads(row["disliked"]),
                "would_return": bool(row["would_return"]),
                "created_at": row["created_at"]
            }
            results.append(feedback)

        return results

    def update_preference(self, category: str, key: str, value: str, confidence: float = 0.5):
        """
        Update a user preference.

        Args:
            category: Preference category (e.g., 'cuisine', 'price_range')
            key: Specific preference key
            value: Preference value
            confidence: Confidence score (0-1)
        """
        pref_id = str(uuid.uuid4())

        with sqlite3.connect(self.db_path) as conn:
            # Try to update existing preference
            result = conn.execute("""
                UPDATE preferences
                SET value = ?, confidence = ?, updated_at = CURRENT_TIMESTAMP
                WHERE category = ? AND key = ?
            """, (value, confidence, category, key))

            # If no rows updated, insert new preference
            if result.rowcount == 0:
                conn.execute("""
                    INSERT INTO preferences (id, category, key, value, confidence)
                    VALUES (?, ?, ?, ?, ?)
                """, (pref_id, category, key, value, confidence))

            conn.commit()

        print(f"[Memory] Updated preference: {category}.{key} = {value} (confidence: {confidence})")

    def get_preferences(self, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Get user preferences.

        Args:
            category: Optional filter by category

        Returns:
            Dictionary of preferences
        """
        query = "SELECT * FROM preferences WHERE 1=1"
        params = []

        if category:
            query += " AND category = ?"
            params.append(category)

        query += " ORDER BY confidence DESC"

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()

        preferences = {}
        for row in rows:
            cat = row["category"]
            if cat not in preferences:
                preferences[cat] = {}

            preferences[cat][row["key"]] = {
                "value": row["value"],
                "confidence": row["confidence"],
                "updated_at": row["updated_at"]
            }

        return preferences

    def log_agent_execution(
        self,
        task_id: str,
        agent_name: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        success: bool,
        duration_ms: int
    ):
        """
        Log an agent execution for auditing and learning.

        Args:
            task_id: Task ID
            agent_name: Name of the agent
            input_data: Input data
            output_data: Output data
            success: Whether execution succeeded
            duration_ms: Duration in milliseconds
        """
        exec_id = str(uuid.uuid4())
        input_json = json.dumps(input_data)
        output_json = json.dumps(output_data)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO agent_executions (id, task_id, agent_name, input, output, success, duration_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (exec_id, task_id, agent_name, input_json, output_json, success, duration_ms))
            conn.commit()

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about stored data.

        Returns:
            Dictionary of statistics
        """
        with sqlite3.connect(self.db_path) as conn:
            stats = {}

            # Count recommendations by type
            cursor = conn.execute("""
                SELECT type, COUNT(*) as count
                FROM recommendations
                GROUP BY type
            """)
            stats["recommendations_by_type"] = {row[0]: row[1] for row in cursor.fetchall()}

            # Count visited vs unvisited
            cursor = conn.execute("""
                SELECT visited, COUNT(*) as count
                FROM recommendations
                GROUP BY visited
            """)
            visited_stats = {row[0]: row[1] for row in cursor.fetchall()}
            stats["visited"] = visited_stats.get(1, 0)
            stats["unvisited"] = visited_stats.get(0, 0)

            # Count feedback
            cursor = conn.execute("SELECT COUNT(*) FROM feedback")
            stats["total_feedback"] = cursor.fetchone()[0]

            # Count preferences
            cursor = conn.execute("SELECT COUNT(*) FROM preferences")
            stats["total_preferences"] = cursor.fetchone()[0]

            # Agent executions
            cursor = conn.execute("SELECT COUNT(*) FROM agent_executions")
            stats["total_executions"] = cursor.fetchone()[0]

        return stats
