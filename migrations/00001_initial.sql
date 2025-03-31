-- +goose Up
-- +goose StatementBegin
CREATE TABLE links
(
    id           SERIAL PRIMARY KEY,
    short_code   VARCHAR(16)              NOT NULL UNIQUE,
    original_url TEXT                     NOT NULL,
    custom_alias BOOLEAN                  NOT NULL DEFAULT FALSE,
    created_at   TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expires_at   TIMESTAMP WITH TIME ZONE,
    CONSTRAINT check_expiry CHECK (expires_at IS NULL OR expires_at > created_at)
);

CREATE TABLE link_visits
(
    id         SERIAL PRIMARY KEY,
    link_id    INTEGER                  NOT NULL REFERENCES links (id) ON DELETE CASCADE,
    visited_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    user_agent TEXT,
    ip_address VARCHAR(45),
    referrer   TEXT
);

CREATE INDEX idx_links_short_code ON links (short_code);
CREATE INDEX idx_links_original_url ON links (original_url);
CREATE INDEX idx_links_expires_at ON links (expires_at);
CREATE INDEX idx_link_visits_link_id ON link_visits (link_id);
CREATE INDEX idx_link_visits_visited_at ON link_visits (visited_at);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP TABLE link_visits CASCADE;
DROP TABLE links CASCADE;
-- +goose StatementEnd
