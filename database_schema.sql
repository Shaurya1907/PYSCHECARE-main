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
-- THERAPISTS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS therapists (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(255) NOT NULL,
    specialty    VARCHAR(255),
    bio          TEXT,
    photo_url    VARCHAR(500),
    -- JSON string: {"monday": ["09:00","10:00"], "tuesday": [...]}
    availability JSON,
    is_active    BOOLEAN DEFAULT TRUE,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed with sample therapists so the booking form works immediately
INSERT IGNORE INTO therapists (id, name, specialty, bio, is_active)
VALUES
    (1, 'Dr. Priya Sharma',    'Anxiety & Depression',    'PhD in Clinical Psychology with 8 years experience.', TRUE),
    (2, 'Dr. Arjun Mehta',     'Trauma & PTSD',           'Certified EMDR practitioner, 6 years experience.',     TRUE),
    (3, 'Dr. Sunita Rao',      'Relationship Counselling', 'Couples and family therapy specialist.',               TRUE),
    (4, 'Dr. Kavya Nair',      'Youth Mental Health',      'Specializes in adolescent and young adult therapy.',   TRUE);


-- ============================================================
-- APPOINTMENTS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS appointments (
    id                   INT AUTO_INCREMENT PRIMARY KEY,
    user_id              INT NOT NULL,
    therapist_id         INT NOT NULL,
    appointment_datetime DATETIME NOT NULL,
    session_type         ENUM('video', 'audio', 'text') NOT NULL DEFAULT 'video',
    notes                TEXT,
    status               ENUM('pending', 'confirmed', 'cancelled', 'completed')
                         NOT NULL DEFAULT 'pending',
    reminder_sent        BOOLEAN DEFAULT FALSE,
    cancellation_reason  VARCHAR(500),
    created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)     REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (therapist_id) REFERENCES therapists(id) ON DELETE RESTRICT,

    -- Fast lookups for a user's upcoming appointments
    INDEX idx_user_upcoming    (user_id, appointment_datetime, status),
    -- Prevent double-booking the same therapist at the same time
    UNIQUE KEY uq_therapist_slot (therapist_id, appointment_datetime)
);