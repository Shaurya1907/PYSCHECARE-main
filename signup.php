<?php
require_once __DIR__ . '/session_config.php';

if ($_SERVER["REQUEST_METHOD"] !== "POST") {
    http_response_code(405);
    exit;
}

if (!isset($_POST['csrf_token']) || !hash_equals($_SESSION['csrf_token'], $_POST['csrf_token'])) {
    die("CSRF token validation failed");
}

$fullname = trim($_POST['fullname'] ?? '');
$email = filter_var(trim($_POST['email'] ?? ''), FILTER_VALIDATE_EMAIL);
$password = $_POST['password'] ?? '';

if (empty($fullname) || !$email || empty($password)) {
    header("Location: signup.html?error=missing_fields");
    exit;
}

if (strlen($fullname) > 100) {
    header("Location: signup.html?error=name_length");
    exit;
}

if (strlen($password) < 8) {
    header("Location: signup.html?error=password_weak");
    exit;
}

$password_hash = password_hash($password, PASSWORD_BCRYPT, ['cost' => 12]);

try {
    $db = new PDO('sqlite:' . __DIR__ . '/database.sqlite');
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    $db->exec("CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )");

    $stmt = $db->prepare("INSERT INTO users (username, email, password_hash) VALUES (:username, :email, :password_hash)");
    $stmt->execute([
        ':username' => $fullname,
        ':email' => $email,
        ':password_hash' => $password_hash
    ]);

    session_regenerate_id(true);
    $_SESSION["username"] = $fullname;
    $_SESSION["logged_in"] = true;
    $_SESSION["login_time"] = time();

    header("Location: welcome.php");
    exit;

} catch (PDOException $e) {
    if (strpos($e->getMessage(), 'UNIQUE') !== false) {
        header("Location: signup.html?error=exists");
        exit;
    }
    error_log("Signup database error: " . $e->getMessage());
    header("Location: signup.html?error=server");
    exit;
}
?>