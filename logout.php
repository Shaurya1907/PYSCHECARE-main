<?php
require_once __DIR__ . '/session_config.php';
session_start();

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    exit('Method Not Allowed. Please use the logout button.');
}

if (empty($_POST['csrf_token']) || $_POST['csrf_token'] !== $_SESSION['csrf_token']) {
    http_response_code(403);
    exit('CSRF token validation failed.');
}

// Destroy all session data
$_SESSION = [];

// Expire the session cookie immediately to prevent session fixation
if (ini_get("session.use_cookies")) {
    $params = session_get_cookie_params();
    setcookie(
        session_name(),
        '',
        time() - 42000,
        $params["path"],
        $params["domain"],
        $params["secure"],
        $params["httponly"]
    );
}

session_destroy();

// Redirect to login with a logout confirmation flag
header("Location: login.html?logged_out=1");
exit();
?>
