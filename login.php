<?php
session_start();
if (empty($_SESSION['csrf_token'])) {
    $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
}

// Check if the form is submitted
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    // Validate CSRF token
    if (empty($_POST['csrf_token']) || !hash_equals($_SESSION['csrf_token'], $_POST['csrf_token'])) {
        http_response_code(403);
        die("Invalid CSRF token.");
    }
    // Get user input
    $username = $_POST["username"];
    $password = $_POST["password"];

    // Connect to local SQLite database (secure DB lookup instead of hardcoded plaintext)
    try {
        $db = new PDO('sqlite:database.sqlite');
        $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        
        // Ensure table exists
        $db->exec("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT)");
        
        // Retrieve the user from the database securely
        $stmt = $db->prepare("SELECT password_hash FROM users WHERE username = :username");
        $stmt->execute([':username' => $username]);
        $user = $stmt->fetch(PDO::FETCH_ASSOC);

        // Verify password hash securely
        if ($user && password_verify($password, $user['password_hash'])) {
            // Successful login
            $_SESSION["username"] = $username;
            header("Location: welcome.php"); // Redirect to a welcome page
            exit();
        } else {
            // Invalid credentials - redirect back to login with error parameter
            header("Location: login.html?error=1");
            exit();
        }
    } catch (PDOException $e) {
        die("Database error: " . $e->getMessage());
    }
}
?>
