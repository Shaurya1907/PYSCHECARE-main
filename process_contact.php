<?php
require_once __DIR__ . '/session_config.php';

if ($_SERVER["REQUEST_METHOD"] !== "POST") {
    http_response_code(405);
    exit;
}

if (!isset($_POST['csrf_token']) || !hash_equals($_SESSION['csrf_token'], $_POST['csrf_token'])) {
    die("CSRF token validation failed");
}

$name = htmlspecialchars(substr($_POST['name'] ?? '', 0, 100), ENT_QUOTES, 'UTF-8');
$email = filter_var(trim($_POST['email'] ?? ''), FILTER_VALIDATE_EMAIL);
$subject = htmlspecialchars(substr($_POST['subject'] ?? '', 0, 200), ENT_QUOTES, 'UTF-8');
$message = htmlspecialchars(substr($_POST['message'] ?? '', 0, 5000), ENT_QUOTES, 'UTF-8');

if (!$email) {
    die("Invalid email address");
}

$to = "support@psychecare.com";
$headers = "From: no-reply@psychecare.com\r\n";
$headers .= "Reply-To: " . $email . "\r\n";
$headers .= "Content-Type: text/html; charset=UTF-8\r\n";

$email_body = "<h2>New Contact Message</h2>
               <p><strong>Name:</strong> {$name}</p>
               <p><strong>Email:</strong> " . htmlspecialchars($email) . "</p>
               <p><strong>Subject:</strong> {$subject}</p>
               <p><strong>Message:</strong><br/>" . nl2br($message) . "</p>";

if (mail($to, $subject, $email_body, $headers)) {
    echo "<script>alert('Message sent successfully!'); window.location.href='index.html';</script>";
} else {
    echo "<script>alert('Failed to send message. Please try again.'); window.history.back();</script>";
}
?>
