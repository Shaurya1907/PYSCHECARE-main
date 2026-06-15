<?php
// session_config.php
// Centralized secure session configuration.
// MUST be included before session_start() in all entry points.

$cookieParams = session_get_cookie_params();
session_set_cookie_params([
    'lifetime' => $cookieParams['lifetime'],
    'path' => '/',
    'domain' => $_SERVER['SERVER_NAME'] ?? '',
    'secure' => isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off', // True if HTTPS
    'httponly' => true, // Prevent JS access to session cookie (mitigates XSS cookie theft)
    'samesite' => 'Strict' // Prevent CSRF attacks by not sending cookie cross-site
]);
?>
