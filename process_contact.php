<?php
require_once __DIR__ . '/session_config.php';
session_start();

if (empty($_SESSION['csrf_token'])) {
    $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {

    // Validate CSRF token
    if (empty($_POST['csrf_token']) || !hash_equals($_SESSION['csrf_token'], $_POST['csrf_token'])) {
        http_response_code(403);
        die("Invalid CSRF token.");
    }

    $name = trim($_POST['name'] ?? '');
    $email = trim($_POST['email'] ?? '');
    $subject = trim($_POST['subject'] ?? '');
    $message = trim($_POST['message'] ?? '');

    if (!$name || !$email || !$subject || !$message) {
        die("All fields are required.");
    }

    if (strlen($name) > 100) {
        die("Name must not exceed 100 characters.");
    }

    if (strlen($email) > 255) {
        die("Email must not exceed 255 characters.");
    }

    if (strlen($subject) > 255) {
        die("Subject must not exceed 255 characters.");
    }

    if (strlen($message) > 1000) {
        die("Message must not exceed 1000 characters.");
    }

    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        die("Invalid email address.");
    }

    $name = htmlspecialchars($name);
    $email = htmlspecialchars($email);
    $subject = htmlspecialchars($subject);
    $message = htmlspecialchars($message);

    try {
        require_once __DIR__ . '/database.php';
        $db = getAuthDatabase();

        $stmt = $db->prepare("INSERT INTO contact_messages (name, email, subject, message) VALUES (:name, :email, :subject, :message)");
        $stmt->execute([
            ':name' => $name,
            ':email' => $email,
            ':subject' => $subject,
            ':message' => $message
        ]);

        echo "Message received. Thank you, $name!";
    } catch (PDOException $e) {
        http_response_code(500);
        die("Database error. Please try again later.");
    }
}
?>
