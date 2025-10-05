-- Soul Mirror Database Schema

CREATE TABLE note_groups (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    custom_rules TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, name)
);

CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    group_id INTEGER NOT NULL REFERENCES note_groups(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_note_groups_user_id ON note_groups(user_id);
CREATE INDEX idx_notes_group_id ON notes(group_id);
CREATE INDEX idx_notes_user_id ON notes(user_id);

-- Requests table to log all incoming requests before agent processing
CREATE TABLE requests (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    input TEXT NOT NULL,
    response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_requests_user_id ON requests(user_id);
CREATE INDEX idx_requests_created_at ON requests(created_at);
