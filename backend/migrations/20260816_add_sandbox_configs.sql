-- Production migration cho UC9.1. Development vẫn dùng Base.metadata.create_all.
CREATE TABLE IF NOT EXISTS sandbox_configs (
    id UUID PRIMARY KEY,
    project_id UUID NOT NULL UNIQUE REFERENCES projects(id) ON DELETE CASCADE,
    db_type VARCHAR(255) NOT NULL DEFAULT 'POSTGRESQL' CHECK (db_type = 'POSTGRESQL'),
    host VARCHAR(255) NOT NULL DEFAULT 'localhost',
    port INTEGER NOT NULL DEFAULT 5432 CHECK (port BETWEEN 1 AND 65535),
    database_name VARCHAR(255) NOT NULL DEFAULT 'sandbox_db',
    username VARCHAR(255),
    password TEXT,
    schema_name VARCHAR(255) DEFAULT 'public'
        CHECK (schema_name IS NULL OR schema_name ~ '^[A-Za-z_][A-Za-z0-9_]*$'),
    status VARCHAR(50) NOT NULL DEFAULT 'CONFIGURED',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);
