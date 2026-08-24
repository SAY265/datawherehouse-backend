-- Giữ nguyên legacy MVP actor nhưng không cấp credential cho các row hiện hữu.
ALTER TABLE users
    ADD COLUMN IF NOT EXISTS password_hash TEXT NULL,
    ADD COLUMN IF NOT EXISTS full_name VARCHAR(150) NULL,
    ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT FALSE;

CREATE UNIQUE INDEX IF NOT EXISTS uq_users_username_casefold
    ON users (LOWER(username));
CREATE UNIQUE INDEX IF NOT EXISTS uq_users_email_casefold
    ON users (LOWER(email));

CREATE TABLE IF NOT EXISTS revoked_auth_tokens (
    id UUID PRIMARY KEY,
    jti VARCHAR(64) NOT NULL UNIQUE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_revoked_auth_tokens_user_id
    ON revoked_auth_tokens (user_id);
CREATE INDEX IF NOT EXISTS idx_revoked_auth_tokens_expires_at
    ON revoked_auth_tokens (expires_at);
