-- Soul Mirror Database Schema

CREATE TABLE note_groups (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    custom_rules TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, name)
);

CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    group_id INTEGER NOT NULL REFERENCES note_groups(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_note_groups_user_id ON note_groups(user_id);
CREATE INDEX idx_notes_group_id ON notes(group_id);
CREATE INDEX idx_notes_user_id ON notes(user_id);

-- Trigger function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to note_groups
CREATE TRIGGER update_note_groups_updated_at BEFORE UPDATE ON note_groups
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Apply trigger to notes
CREATE TRIGGER update_notes_updated_at BEFORE UPDATE ON notes
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Requests table to log all incoming requests before agent processing
CREATE TABLE requests (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    input TEXT NOT NULL,
    response TEXT,
    llm_traces JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_requests_user_id ON requests(user_id);
CREATE INDEX idx_requests_created_at ON requests(created_at);

-- Core memory table - stores agent's long-term understanding of each user
CREATE TABLE core_memory (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL UNIQUE,
    content TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_core_memory_user_id ON core_memory(user_id);

-- Apply trigger to core_memory
CREATE TRIGGER update_core_memory_updated_at BEFORE UPDATE ON core_memory
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Responsibilities table - agent's internal workflows and tasks
CREATE TABLE responsibilities (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_responsibilities_user_id ON responsibilities(user_id);

-- Apply trigger to responsibilities
CREATE TRIGGER update_responsibilities_updated_at BEFORE UPDATE ON responsibilities
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
