<?php
require_once __DIR__ . '/session_config.php';
require_once __DIR__ . '/validation.php';
require_once __DIR__ . '/sanitize.php';
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

    $error = validateContactInput($name, $email, $subject, $message);
    if ($error !== null) {
        http_response_code(400);
        die(json_encode(['success' => false, 'error' => $error]));
    }

    try {
        require_once __DIR__ . '/database.php';
        $db = getAuthDatabase();

        $ip = $_SERVER['REMOTE_ADDR'] ?? '';
        if (!enforceRateLimit($db, "contact:" . $ip, 5, 60)) {
            http_response_code(429);
            die("Too many contact attempts. Please try again later.");
        }

        $stmt = $db->prepare("INSERT INTO contact_messages (name, email, subject, message) VALUES (:name, :email, :subject, :message)");
        $stmt->execute([
            ':name' => $name,
            ':email' => $email,
            ':subject' => $subject,
            ':message' => $message
        ]);

        echo "Message received. Thank you, " . e($name) . "!";
    } catch (PDOException $e) {
        http_response_code(500);
        echo json_encode(['success' => false, 'error' => 'Database error. Please try again later.']);
    }
}
?>
