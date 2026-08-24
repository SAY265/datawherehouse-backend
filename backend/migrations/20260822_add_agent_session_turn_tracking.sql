ALTER TABLE project_sessions
    ADD COLUMN IF NOT EXISTS active_turn_id UUID NULL,
    ADD COLUMN IF NOT EXISTS active_turn_started_at TIMESTAMPTZ NULL;

ALTER TABLE session_events
    ADD COLUMN IF NOT EXISTS turn_id UUID NULL;

CREATE INDEX IF NOT EXISTS idx_session_events_turn_id
    ON session_events (turn_id);

CREATE INDEX IF NOT EXISTS idx_session_events_session_turn
    ON session_events (session_id, turn_id);
