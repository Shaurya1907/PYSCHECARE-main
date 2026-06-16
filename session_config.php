<?php
// session_config.php
// Centralized secure session configuration.
// MUST be included before session_start() in all entry points.

ini_set('session.gc_maxlifetime', 1800); // 30 minutes garbage collection
ini_set('session.use_strict_mode', 1); // Prevent session adoption

$cookieParams = session_get_cookie_params();
session_set_cookie_params([
    'lifetime' => 0, // Session expires on browser close
    'path' => '/',
    'domain' => $_SERVER['SERVER_NAME'] ?? '',
    'secure' => isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off', // True if HTTPS
    'httponly' => true, // Prevent JS access to session cookie
    'samesite' => 'Strict' // Prevent CSRF attacks by not sending cookie cross-site
]);
?>
