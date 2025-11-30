-- Database schema for the multi-agent system

-- Recommendations (restaurants, events, places)
CREATE TABLE IF NOT EXISTS recommendations (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,  -- 'restaurant', 'event', 'place'
    name TEXT NOT NULL,
    location TEXT,
    metadata JSON,  -- All other data stored as JSON
    source_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    visited BOOLEAN DEFAULT FALSE
);

-- User feedback
CREATE TABLE IF NOT EXISTS feedback (
    id TEXT PRIMARY KEY,
    recommendation_id TEXT,
    rating INTEGER,  -- 1-5
    notes TEXT,
    liked TEXT,  -- JSON array of liked aspects
    disliked TEXT,  -- JSON array of disliked aspects
    would_return BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recommendation_id) REFERENCES recommendations(id)
);

-- User preferences (learned over time)
CREATE TABLE IF NOT EXISTS preferences (
    id TEXT PRIMARY KEY,
    category TEXT NOT NULL,  -- 'cuisine', 'price_range', 'location', etc.
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    confidence FLOAT DEFAULT 0.5,  -- How confident we are (0-1)
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(category, key)
);

-- Deals and offers
CREATE TABLE IF NOT EXISTS deals (
    id TEXT PRIMARY KEY,
    recommendation_id TEXT,
    description TEXT,
    discount_amount TEXT,
    valid_until TIMESTAMP,
    source_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recommendation_id) REFERENCES recommendations(id)
);

-- Agent task executions (for auditing and learning)
CREATE TABLE IF NOT EXISTS agent_executions (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    input JSON,
    output JSON,
    success BOOLEAN,
    duration_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_recommendations_type ON recommendations(type);
CREATE INDEX IF NOT EXISTS idx_recommendations_visited ON recommendations(visited);
CREATE INDEX IF NOT EXISTS idx_recommendations_created_at ON recommendations(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_feedback_recommendation ON feedback(recommendation_id);
CREATE INDEX IF NOT EXISTS idx_preferences_category ON preferences(category);
CREATE INDEX IF NOT EXISTS idx_agent_executions_agent ON agent_executions(agent_name);
CREATE INDEX IF NOT EXISTS idx_agent_executions_task ON agent_executions(task_id);
