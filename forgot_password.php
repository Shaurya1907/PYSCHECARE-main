<?php
require_once __DIR__ . '/session_config.php';
session_start();

require_once __DIR__ . '/database.php';

if ($_SERVER["REQUEST_METHOD"] !== "POST") {
    header("Location: forgot_password.html");
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

$email = trim($_POST["email"] ?? "");

if ($email === "" || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
    header("Location: forgot_password.html?error=invalid_email");
    exit();
}

$db = getAuthDatabase();
$ip = getIPAddress();
$rateKey = "forgot_pwd:" . $ip;

if (!enforceRateLimit($db, $rateKey, 3, 900)) {
    header("Location: forgot_password.html?error=rate_limit");
    exit();
}

$stmt = $db->prepare("SELECT id FROM users WHERE email = :email");
$stmt->execute([':email' => $email]);
$user = $stmt->fetch();

if ($user) {
    $token = bin2hex(random_bytes(32));
    $tokenHash = hash('sha256', $token);
    $expiresAt = time() + 3600;

    $stmt = $db->prepare(
        "INSERT INTO password_resets (email, token_hash, expires_at) VALUES (:email, :token_hash, :expires_at)"
    );
    $stmt->execute([
        ':email'      => $email,
        ':token_hash'  => $tokenHash,
        ':expires_at'  => $expiresAt,
    ]);

    $resetLink = (isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on' ? 'https' : 'http')
        . "://" . $_SERVER['HTTP_HOST']
        . rtrim(dirname($_SERVER['SCRIPT_NAME']), '/\\') . "/"
        . "reset_password.php?token=" . rawurlencode($token);

    $subject = "PsycheCare Password Reset";
    $message = "You requested a password reset.\n\n"
             . "Click the link below to reset your password (expires in 1 hour):\n\n"
             . $resetLink . "\n\n"
             . "If you did not request this, please ignore this email.";
    mail($email, $subject, $message, "From: noreply@psychecare.local");
}

header("Location: forgot_password.html?sent=1");
exit();
