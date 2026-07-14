CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    failed_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS contact_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    subject TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS rate_limiting (
    rate_key TEXT PRIMARY KEY,
    attempts INTEGER DEFAULT 0,
    last_attempt INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS password_resets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    token_hash TEXT NOT NULL UNIQUE,
    expires_at INTEGER NOT NULL,
    used INTEGER NOT NULL DEFAULT 0
);

-- ============================================================
-- MOOD JOURNAL TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS mood_journal (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    user_id      INT NOT NULL,
    mood_score   TINYINT NOT NULL CHECK (mood_score BETWEEN 1 AND 10),
    mood_label   VARCHAR(50) NOT NULL,
    journal_text TEXT,
    logged_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    entry_date   DATE NOT NULL,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,

    -- One entry per user per day
    UNIQUE KEY unique_daily_entry (user_id, entry_date),

    -- Fast lookup for streak calculation
    INDEX idx_user_date (user_id, entry_date)
);