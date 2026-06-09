<?php
require_once __DIR__ . '/../session_config.php';
/**
 * chatBot.php — Authentication gateway for the PsycheCare chatbot page.
 *
 * This file REPLACES direct access to chatBot.html.
 * It verifies the user's PHP session before serving the chatbot interface.
 * Unauthenticated users are redirected to the login page.
 */

session_start();

// If the user is not logged in, redirect them to login with a return URL
if (!isset($_SESSION['username'])) {
    header('Location: ../login.html?next=chatBot');
    exit();
}

// User is authenticated — inject their username and a signed chat token
// The chat token is a one-time HMAC derived from the session ID and a server secret.
// It is passed to the browser and sent as an Authorization header on every API call.
$secret       = getenv('CHAT_API_SECRET') ?: 'change-me-in-production';
$session_id   = session_id();
$username     = htmlspecialchars($_SESSION['username'], ENT_QUOTES, 'UTF-8');
$payload      = base64_encode($session_id . '|' . $username);
$signature    = hash_hmac('sha256', $payload, $secret);
$chat_token   = $payload . '.' . $signature;

// Serve the chatbot HTML, injecting auth context as a window config object
// so the JavaScript can attach the token to every API request.
$html = file_get_contents(__DIR__ . '/chatBot.html');

// Inject window config right before </head>
$injection = <<<JS
    <script>
        // Injected by chatBot.php — DO NOT expose or log these values
        window.PSYCHECARE_USER    = {$_SESSION['username'] ? json_encode($username) : 'null'};
        window.PSYCHECARE_TOKEN   = "{$chat_token}";
    </script>
JS;

$html = str_replace('</head>', $injection . '</head>', $html);
echo $html;
?>
