<?php
session_start();

try {
    $db = new PDO('sqlite:' . __DIR__ . '/users.db');
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    error_log("Database error: " . $e->getMessage());
    http_response_code(500);
    die("An internal error occurred. Please try again later.");
}

// Create tables if they don't exist
$db->exec("
    CREATE TABLE IF NOT EXISTS users (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        username      TEXT    NOT NULL UNIQUE,
        password_hash TEXT    NOT NULL
    );

    CREATE TABLE IF NOT EXISTS login_attempts (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        username     TEXT    NOT NULL,
        ip_address   TEXT    NOT NULL,
        attempt_time INTEGER NOT NULL
    );

    CREATE INDEX IF NOT EXISTS idx_la_user_time
        ON login_attempts (username, attempt_time);

    CREATE INDEX IF NOT EXISTS idx_la_ip_time
        ON login_attempts (ip_address, attempt_time);
");

// ── Constants ────────────────────────────────────────────────────────────────
define('MAX_ATTEMPTS',    5);    // failures allowed per window
define('LOCKOUT_WINDOW', 900);   // 15 minutes in seconds

// ── Helpers ──────────────────────────────────────────────────────────────────

/**
 * Count recent failed logins for a username OR an IP address.
 * Both checks run so credential-stuffing across accounts is also blocked.
 */
function recentFailures(PDO $db, string $username, string $ip): int {
    $cutoff = time() - LOCKOUT_WINDOW;

    $byUser = $db->prepare(
        "SELECT COUNT(*) FROM login_attempts
          WHERE username = :u AND attempt_time > :t"
    );
    $byUser->execute([':u' => $username, ':t' => $cutoff]);

    $byIp = $db->prepare(
        "SELECT COUNT(*) FROM login_attempts
          WHERE ip_address = :ip AND attempt_time > :t"
    );
    $byIp->execute([':ip' => $ip, ':t' => $cutoff]);

    return max((int)$byUser->fetchColumn(), (int)$byIp->fetchColumn());
}

/**
 * Record a failed login attempt.
 */
function recordFailure(PDO $db, string $username, string $ip): void {
    $stmt = $db->prepare(
        "INSERT INTO login_attempts (username, ip_address, attempt_time)
         VALUES (:u, :ip, :t)"
    );
    $stmt->execute([':u' => $username, ':ip' => $ip, ':t' => time()]);
}

/**
 * Remove attempts older than the lockout window (call this periodically
 * or on every request — cheap because of the index).
 */
function pruneOldAttempts(PDO $db): void {
    $db->prepare(
        "DELETE FROM login_attempts WHERE attempt_time < :cutoff"
    )->execute([':cutoff' => time() - LOCKOUT_WINDOW]);
}

// ── Request handling ─────────────────────────────────────────────────────────

$error = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {

    $username = trim($_POST['username'] ?? '');
    $password = $_POST['password'] ?? '';
    $ip       = $_SERVER['REMOTE_ADDR'];

    pruneOldAttempts($db);

    // 1. Rate-limit check (username AND ip)
    if (recentFailures($db, $username, $ip) >= MAX_ATTEMPTS) {
        http_response_code(429);
        $error = 'Too many failed attempts. Please try again in 15 minutes.';

    } else {
        // 2. Look up user
        $stmt = $db->prepare(
            "SELECT password_hash FROM users WHERE username = :u LIMIT 1"
        );
        $stmt->execute([':u' => $username]);
        $row = $stmt->fetch(PDO::FETCH_ASSOC);

        // 3. Verify password with constant-time comparison
        //    password_verify() always runs even when no user exists,
        //    preventing timing-based username enumeration.
        $dummyHash  = '$2y$12$invalidhashfortimingpurposesonly000000000000000000000000u';
        $storedHash = $row ? $row['password_hash'] : $dummyHash;
        $valid      = $row && password_verify($password, $storedHash);

        if ($valid) {
            // Successful login — regenerate session ID to prevent fixation
            session_regenerate_id(true);
            $_SESSION['username'] = $username;
            header('Location: welcome.php');
            exit();
        } else {
            recordFailure($db, $username, $ip);
            // Generic message — don't reveal whether username exists
            $error = 'Invalid username or password.';
        }
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Login</title>
</head>
<body>
    <?php if ($error): ?>
        <p style="color:red;"><?= htmlspecialchars($error) ?></p>
    <?php endif; ?>

    <form method="POST" action="">
        <label>Username <input type="text"     name="username" required autocomplete="username"></label><br>
        <label>Password <input type="password" name="password" required autocomplete="current-password"></label><br>
        <button type="submit">Log in</button>
    </form>
</body>
</html>