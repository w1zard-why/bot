-- bot/app/db/schema.sql
CREATE TABLE IF NOT EXISTS users (
    id            BIGINT PRIMARY KEY,
    username      TEXT    NOT NULL,
    created_at    TIMESTAMPTZ DEFAULT now(),
    auto_enabled  BOOLEAN NOT NULL DEFAULT TRUE,
    interval_min  INT     NOT NULL DEFAULT 15
);

CREATE TABLE IF NOT EXISTS balances (
    user_id BIGINT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    stars   INT    NOT NULL
);

CREATE TABLE IF NOT EXISTS purchases (
    id           SERIAL  PRIMARY KEY,
    user_id      BIGINT  REFERENCES users(id) ON DELETE CASCADE,
    gift_id      TEXT    NOT NULL,
    gift_name    TEXT    NOT NULL,
    spent        INT     NOT NULL,
    purchased_at BIGINT  NOT NULL DEFAULT (extract(epoch FROM now()))
);

CREATE TABLE IF NOT EXISTS payments (
    invoice_id TEXT PRIMARY KEY,
    user_id    BIGINT REFERENCES users(id) ON DELETE CASCADE,
    stars      INT    NOT NULL
);

CREATE TABLE IF NOT EXISTS gifts_settings (
    gift_id    TEXT PRIMARY KEY,
    target_qty INT  NOT NULL DEFAULT 1,
    max_price  INT  NOT NULL DEFAULT 50
);
