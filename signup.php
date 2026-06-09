<?php
require_once __DIR__ . '/session_config.php';

session_start();

require_once __DIR__ . '/database.php';

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    // Validate CSRF token
    if (
        empty($_POST['csrf_token']) ||
        empty($_SESSION['csrf_token']) ||
        !hash_equals($_SESSION['csrf_token'], $_POST['csrf_token'])
    ) {
        die("CSRF token validation failed");
    }

    // Get user input
    $username = trim($_POST["username"]);
    $email = trim($_POST["email"]);
    $password = $_POST["password"];

    // Validate inputs
    if (empty($username) || empty($email) || empty($password)) {
        header("Location: signup.html?error=empty");
        exit();
    }

    // Enforce minimum password length server-side (never trust frontend alone)
    if (strlen($password) < 8) {
        header("Location: signup.html?error=weak_password");
        exit();
    }

    // Validate email format
    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        header("Location: signup.html?error=email");
        exit();
    }

    // Connect to local SQLite database
    try {
        $db = getAuthDatabase();
        $ip = getIPAddress();
        $rateKey = "signup:" . $ip;

        // Check AND Increment atomically: 3 attempts per hour
        if (!enforceRateLimit($db, $rateKey, 3, 3600)) {
            header("Location: signup.html?error=rate_limit");
            exit();
        }

        // Check if username already exists
        $stmt = $db->prepare("SELECT id FROM users WHERE username = :username");
        $stmt->execute([':username' => $username]);
        if ($stmt->fetch()) {
            header("Location: signup.html?error=exists");
            exit();
        }

        // Check if email already exists
        $stmt = $db->prepare("SELECT id FROM users WHERE email = :email");
        $stmt->execute([':email' => $email]);
        if ($stmt->fetch()) {
            header("Location: signup.html?error=email_exists");
            exit();
        }
        // Hash password securely with explicit cost to match login script
        $password_hash = password_hash($password, PASSWORD_BCRYPT, ['cost' => 12]);

        // Insert new user
        $stmt = $db->prepare(
            "INSERT INTO users (username, email, password_hash) VALUES (:username, :email, :password_hash)"
        );
        $stmt->execute([
            ':username' => $username,
            ':email' => $email,
            ':password_hash' => $password_hash
        ]);

        // Reset rate limit on success
        resetAttempts($db, $rateKey);

        // Automatically log in user after successful signup
        session_regenerate_id(true);
        $_SESSION["user_id"] = $db->lastInsertId();
        $_SESSION["username"] = $username;
        header("Location: welcome.php");
        exit();
    } catch (PDOException $e) {
        header("Location: signup.html?error=db");
        exit();
    }
} else {
    header("Location: signup.html");
    exit();
}
