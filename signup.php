<?php

session_start();

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    // Validate CSRF token
    if (!isset($_POST['csrf_token']) || $_POST['csrf_token'] !== $_SESSION['csrf_token']) {
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

    // Validate email format
    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        header("Location: signup.html?error=email");
        exit();
    }

    // Connect to local SQLite database
    try {
        $db = new PDO('sqlite:database.sqlite');
        $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

        // Ensure table exists
        $db->exec(
            "CREATE TABLE IF NOT EXISTS users " .
            "(id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT)"
        );

        // Check if username already exists
        $stmt = $db->prepare("SELECT id FROM users WHERE username = :username");
        $stmt->execute([':username' => $username]);
        if ($stmt->fetch()) {
            header("Location: signup.html?error=exists");
            exit();
        }

        // Hash password securely
        $password_hash = password_hash($password, PASSWORD_DEFAULT);

        // Insert new user
        $stmt = $db->prepare(
            "INSERT INTO users (username, password_hash) VALUES (:username, :password_hash)"
        );
        $stmt->execute([
            ':username' => $username,
            ':password_hash' => $password_hash
        ]);

        // Automatically log in user after successful signup
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
