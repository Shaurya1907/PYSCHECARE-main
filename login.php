<?php
require_once __DIR__ . '/session_config.php';
session_start();

require_once __DIR__ . '/database.php';

if ($_SERVER["REQUEST_METHOD"] !== "POST") {
    header("Location: login.html");
    exit();
}

if (
    empty($_POST['csrf_token']) ||
    empty($_SESSION['csrf_token']) ||
    !hash_equals($_SESSION['csrf_token'], $_POST['csrf_token'])
) {
    http_response_code(403);
    die("Invalid CSRF token.");
}

$username = trim($_POST["username"] ?? "");
$password = $_POST["password"] ?? "";

if ($username === "" || $password === "") {
    header("Location: login.html?error=invalid");
    exit();
}

try {
    $db  = getAuthDatabase();
    $ip  = getIPAddress();
    $rateKey = "login:" . $ip;

    // Check AND Increment atomically: 5 attempts per 15 minutes
    if (!enforceRateLimit($db, $rateKey, 5, 900)) {
        header("Location: login.html?error=rate_limit");
        exit();
    }

    // ── Layer 1: IP-based rate limit (5 attempts per 15 min per IP) ───────────
    // enforceRateLimit is already atomic and sufficient for this layer.
    $stmt = $db->prepare(
        "SELECT id, username, password_hash FROM users WHERE username = :username"
    );
    $stmt->execute([':username' => $username]);
    $user = $stmt->fetch();

    // ── Layer 2: Per-account lockout (5 failed attempts → 15 min lock) ───────
    // Check BEFORE password_verify so locked accounts get no timing hint.
    if ($user && isAccountLocked($db, $user['id'])) {
        $remaining = max(0, getAccountLockExpiry($db, $user['id']) - time());
        $minutes   = (int) ceil($remaining / 60);
        header("Location: login.html?error=locked&minutes=" . $minutes);
        exit();
    }

    // ── Verify password ───────────────────────────────────────────────────────
    if ($user && password_verify($password, $user['password_hash'])) {
        // Success — clear all lockout state and regenerate session
        clearAccountLock($db, $user['id']);
        resetAttempts($db, $rateKey);
        session_regenerate_id(true);
        $_SESSION["user_id"]  = $user["id"];
        $_SESSION["username"] = $user["username"];
        header("Location: welcome.php");
        exit();
    }

    // Failed attempt is already recorded atomically by enforceRateLimit.
    // If we reach here, it's just a regular invalid password.
    if ($user) {
        incrementAccountAttempts($db, $user['id']); // Account counter
    }

} catch (PDOException $e) {
    header("Location: login.html?error=db");
    exit();
}

header("Location: login.html?error=invalid");
exit();
