<?php

function getAuthDatabase(): PDO
{
    $db = new PDO('sqlite:' . __DIR__ . '/database.sqlite');
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $db->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);

    return $db;
}

function getIPAddress(): string
{
    return $_SERVER['REMOTE_ADDR'] ?? 'unknown';
}

function enforceRateLimit(PDO $db, string $key, int $maxAttempts, int $windowSeconds): bool
{
    $now = time();
    $expired = $now - $windowSeconds;

    // 1. Clean up expired attempts
    $stmt = $db->prepare("DELETE FROM rate_limiting WHERE rate_key = :key AND last_attempt <= :expired");
    $stmt->execute([':key' => $key, ':expired' => $expired]);

    // 2. Increment atomically
    $stmt = $db->prepare("
        INSERT INTO rate_limiting (rate_key, attempts, last_attempt) 
        VALUES (:key, 1, :now)
        ON CONFLICT(rate_key) DO UPDATE SET 
            attempts = attempts + 1,
            last_attempt = :now
    ");
    $stmt->execute([':key' => $key, ':now' => $now]);

    // 3. Read back the new atomic value
    $stmt = $db->prepare("SELECT attempts FROM rate_limiting WHERE rate_key = :key");
    $stmt->execute([':key' => $key]);
    $row = $stmt->fetch();

    return ($row && $row['attempts'] <= $maxAttempts);
}

function resetAttempts(PDO $db, string $key): void
{
    $stmt = $db->prepare("DELETE FROM rate_limiting WHERE rate_key = :key");
    $stmt->execute([':key' => $key]);
}

// ── Per-account lockout helpers ───────────────────────────────────────────────
// Tracks failed attempts per user ID (not IP) so attackers cannot bypass
// lockout by changing IP or rotating proxies.

const MAX_ACCOUNT_ATTEMPTS = 5;
const ACCOUNT_LOCKOUT_SECONDS = 900; // 15 minutes

function isAccountLocked(PDO $db, int $userId): bool
{
    $stmt = $db->prepare('SELECT locked_until FROM users WHERE id = :id');
    $stmt->execute([':id' => $userId]);
    $row = $stmt->fetch();
    return $row && $row['locked_until'] > time();
}

function getAccountLockExpiry(PDO $db, int $userId): int
{
    $stmt = $db->prepare('SELECT locked_until FROM users WHERE id = :id');
    $stmt->execute([':id' => $userId]);
    $row = $stmt->fetch();
    return $row ? (int)$row['locked_until'] : 0;
}

function incrementAccountAttempts(PDO $db, int $userId): void
{
    $db->prepare("
        UPDATE users
        SET failed_attempts = failed_attempts + 1,
            locked_until   = CASE
                WHEN failed_attempts + 1 >= :max
                THEN :lockUntil
                ELSE locked_until
            END
        WHERE id = :id
    ")->execute([
        ':max'       => MAX_ACCOUNT_ATTEMPTS,
        ':lockUntil' => time() + ACCOUNT_LOCKOUT_SECONDS,
        ':id'        => $userId,
    ]);
}

function clearAccountLock(PDO $db, int $userId): void
{
    $db->prepare("
        UPDATE users SET failed_attempts = 0, locked_until = 0 WHERE id = :id
    ")->execute([':id' => $userId]);
}
