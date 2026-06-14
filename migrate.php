<?php

function runMigrations(): void
{
    $db = new PDO('sqlite:' . __DIR__ . '/database.sqlite');
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $db->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);

    echo "Running migrations...\n";

    $db->exec(
        "CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            failed_attempts INTEGER NOT NULL DEFAULT 0,
            locked_until INTEGER NOT NULL DEFAULT 0
        )"
    );

    // Migrate existing users table if columns are missing
    $cols = array_column($db->query('PRAGMA table_info(users)')->fetchAll(), 'name');
    if (!in_array('failed_attempts', $cols)) {
        $db->exec('ALTER TABLE users ADD COLUMN failed_attempts INTEGER NOT NULL DEFAULT 0');
        echo "Added failed_attempts to users.\n";
    }
    if (!in_array('locked_until', $cols)) {
        $db->exec('ALTER TABLE users ADD COLUMN locked_until INTEGER NOT NULL DEFAULT 0');
        echo "Added locked_until to users.\n";
    }

    $db->exec(
        "CREATE TABLE IF NOT EXISTS contact_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            subject TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )"
    );

    $contactCols = array_column($db->query('PRAGMA table_info(contact_messages)')->fetchAll(), 'name');
    if (!in_array('subject', $contactCols)) {
        $db->exec('ALTER TABLE contact_messages ADD COLUMN subject TEXT NOT NULL DEFAULT ""');
        echo "Added subject to contact_messages.\n";
    }

    $db->exec(
        "CREATE TABLE IF NOT EXISTS rate_limiting (
            rate_key TEXT PRIMARY KEY,
            attempts INTEGER DEFAULT 0,
            last_attempt INTEGER DEFAULT 0
        )"
    );

    echo "Migrations completed successfully.\n";
}

runMigrations();
