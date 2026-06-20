<?php

function getAuthDatabase(): PDO
{
    $db = new PDO('sqlite:' . __DIR__ . '/database.sqlite');
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $db->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);

    return $db;
}

// ── Secure Database Abstraction Layer ─────────────────────────────────────────

class SecureDatabaseManager
{
    private PDO $connection;

    public function __construct(PDO $pdo)
    {
        $this->connection = $pdo;
    }

    /**
     * Executes a secure prepared statement to prevent SQL Injection.
     * Enforces the usage of parameters exclusively.
     * 
     * @param string $query The SQL query with placeholders
     * @param array $params An associative array of parameters
     * @return PDOStatement The executed statement
     * @throws Exception If parameters are missing for a parameterized query
     */
    public function executeQuerySecure(string $query, array $params = []): PDOStatement
    {
        if (strpos($query, ':') !== false && empty($params)) {
            error_log("Security Exception: Query contains placeholders but no parameters were provided.");
            throw new Exception("SQL Injection Prevention: Parameters must be provided for parameterized queries.");
        }

        try {
            $stmt = $this->connection->prepare($query);
            foreach ($params as $key => $value) {
                // Ensure strict typing for bound parameters to prevent type juggling attacks
                $type = PDO::PARAM_STR;
                if (is_int($value)) {
                    $type = PDO::PARAM_INT;
                } elseif (is_bool($value)) {
                    $type = PDO::PARAM_BOOL;
                } elseif (is_null($value)) {
                    $type = PDO::PARAM_NULL;
                }
                
                $stmt->bindValue($key, $value, $type);
            }
            
            $stmt->execute();
            return $stmt;
            
        } catch (PDOException $e) {
            error_log("Database execution error securely caught: " . $e->getMessage());
            throw new Exception("A database error occurred. Please try again later.");
        }
    }
    
    public function fetchOne(string $query, array $params = []): ?array
    {
        $stmt = $this->executeQuerySecure($query, $params);
        $result = $stmt->fetch();
        return $result ?: null;
    }
    
    public function fetchAll(string $query, array $params = []): array
    {
        $stmt = $this->executeQuerySecure($query, $params);
        return $stmt->fetchAll();
    }
}

function getIPAddress(): string
{
    if (!empty($_SERVER['HTTP_X_FORWARDED_FOR'])) {
        // Extract the client IP from a comma-separated list of IPs
        $ipList = explode(',', $_SERVER['HTTP_X_FORWARDED_FOR']);
        return trim($ipList[0]);
    }
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

// ── Profile and IDOR Protection ─────────────────────────────────────────────

function getUserProfileSecure(PDO $db, int $targetUserId, int $requestingUserId): ?array
{
    // IDOR Protection: Ensure the user requesting the profile is the owner
    // This strict ownership validation layer prevents unauthorized access.
    if ($targetUserId !== $requestingUserId) {
        // Log this unauthorized access attempt securely
        error_log("IDOR Attack Prevented: User $requestingUserId attempted to access profile $targetUserId");
        throw new Exception("Unauthorized access to user profile. IDOR protection triggered.");
    }

    $secureDb = new SecureDatabaseManager($db);
    $row = $secureDb->fetchOne('SELECT id, username, email, created_at FROM users WHERE id = :id', [':id' => $targetUserId]);
    
    if (!$row) {
        return null;
    }
    
    return [
        'id' => $row['id'],
        'username' => $row['username'],
        'email' => $row['email'],
        'joined' => $row['created_at'] ?? 'Unknown'
    ];
}

function updateProfileEmailSecure(PDO $db, int $targetUserId, int $requestingUserId, string $newEmail): bool
{
    // Strict ownership validation to prevent IDOR on profile updates
    if ($targetUserId !== $requestingUserId) {
        error_log("IDOR Attack Prevented: User $requestingUserId attempted to update profile $targetUserId");
        return false;
    }

    if (!filter_var($newEmail, FILTER_VALIDATE_EMAIL)) {
        return false;
    }

    $stmt = $db->prepare('UPDATE users SET email = :email WHERE id = :id');
    return $stmt->execute([
        ':email' => $newEmail,
        ':id' => $targetUserId
    ]);
}
