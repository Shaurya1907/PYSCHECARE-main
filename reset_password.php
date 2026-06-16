<?php
require_once __DIR__ . '/session_config.php';
require_once __DIR__ . '/sanitize.php';
session_start();

require_once __DIR__ . '/database.php';

if ($_SERVER["REQUEST_METHOD"] === "POST") {
    if (
        empty($_POST['csrf_token']) ||
        empty($_SESSION['csrf_token']) ||
        !hash_equals($_SESSION['csrf_token'], $_POST['csrf_token'])
    ) {
        http_response_code(403);
        die("Invalid CSRF token.");
    }

    $token = $_POST["token"] ?? "";
    $password = $_POST["password"] ?? "";
    $confirm = $_POST["confirm_password"] ?? "";

    if ($token === "" || $password === "" || $confirm === "") {
        header("Location: reset_password.php?token=" . rawurlencode($token) . "&error=missing");
        exit();
    }

    if ($password !== $confirm) {
        header("Location: reset_password.php?token=" . rawurlencode($token) . "&error=mismatch");
        exit();
    }

    if (strlen($password) < 8) {
        header("Location: reset_password.php?token=" . rawurlencode($token) . "&error=weak");
        exit();
    }

    $db = getAuthDatabase();
    $ip = getIPAddress();
    $rateKey = "reset_pwd:" . $ip;

    if (!enforceRateLimit($db, $rateKey, 3, 900)) {
        header("Location: reset_password.php?token=" . rawurlencode($token) . "&error=rate_limit");
        exit();
    }

    $tokenHash = hash('sha256', $token);

    $stmt = $db->prepare(
        "SELECT email FROM password_resets WHERE token_hash = :token_hash AND expires_at > :now AND used = 0"
    );
    $stmt->execute([':token_hash' => $tokenHash, ':now' => time()]);
    $row = $stmt->fetch();

    if (!$row) {
        header("Location: forgot_password.html?error=invalid_token");
        exit();
    }

    $email = $row['email'];
    $newHash = password_hash($password, PASSWORD_DEFAULT);

    $db->prepare("UPDATE users SET password_hash = :hash WHERE email = :email")
        ->execute([':hash' => $newHash, ':email' => $email]);

    $db->prepare("UPDATE password_resets SET used = 1 WHERE token_hash = :token_hash")
        ->execute([':token_hash' => $tokenHash]);

    session_regenerate_id(true);
    header("Location: login.html?password_reset=1");
    exit();
}

$token = $_GET["token"] ?? "";
if ($token === "") {
    header("Location: forgot_password.html");
    exit();
}

$db = getAuthDatabase();
$tokenHash = hash('sha256', $token);

$stmt = $db->prepare(
    "SELECT email FROM password_resets WHERE token_hash = :token_hash AND expires_at > :now AND used = 0"
);
$stmt->execute([':token_hash' => $tokenHash, ':now' => time()]);
$row = $stmt->fetch();

if (!$row) {
    header("Location: forgot_password.html?error=invalid_token");
    exit();
}
?><!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Set New Password | PsycheCare</title>

    <script src="https://kit.fontawesome.com/1b2b6a64da.js" crossorigin="anonymous"></script>

    <link rel="stylesheet" href="style.css">
    <link rel="icon" href="Images/B_icon01.png">
    <style>
        .reset-container {
            max-width: 400px;
            margin: 100px auto;
            padding: 2rem;
            background-color: var(--light-color);
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(127, 90, 240, 0.2);
            animation: fadeIn 0.8s ease forwards;
        }

        .reset-header {
            text-align: center;
            margin-bottom: 2rem;
        }

        .form-group {
            margin-bottom: 1.5rem;
        }

        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            color: var(--dark-color);
            font-weight: 500;
        }

        .form-group input {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-family: 'Poppins', sans-serif;
            transition: border-color 0.3s;
            box-sizing: border-box;
        }

        .form-group input:focus {
            outline: none;
            border-color: var(--primary-color);
        }

        .reset-btn {
            background-color: var(--primary-color);
            color: white;
            border: none;
            padding: 0.75rem;
            border-radius: 5px;
            font-family: 'Poppins', sans-serif;
            font-weight: 500;
            cursor: pointer;
            transition: background-color 0.3s;
            width: 100%;
        }

        .reset-btn:hover {
            background-color: #6a4cc7;
        }

        .return-links {
            text-align: center;
            margin-top: 1rem;
        }

        .return-links a {
            color: var(--primary-color);
            text-decoration: none;
        }

        .return-links a:hover {
            text-decoration: underline;
        }

        .error-message {
            color: #e74c3c;
            font-size: 0.9rem;
            margin-top: 0.5rem;
            text-align: center;
            display: none;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo-cantainer">
            <h2 class="logo">PsycheCare.</h2>
        </div>
        <div class="nav-and-btn-cont">
            <div class="nav-list-cont">
                <ul class="nav-ul">
                    <li><a href="index.html">HOME</a></li>
                    <li><a href="index.html#section-3">CHAT BOT</a></li>
                    <li><a href="otherHTML/statistics.html">STATISTICS</a></li>
                    <li><a href="index.html#footer">CONTACT</a></li>
                    <li><a href="login.html">LOGIN</a></li>
                </ul>
            </div>
            <div class="hamburger">
                <diV class="line line1"></diV>
                <div class="mid-line-cont">
                    <div class="line mid-line1"></div>
                    <div class="line mid-line2"></div>
                </div>
                <diV class="line line3"></diV>
            </div>
        </div>
    </div>

    <div class="mobile-view-nav-cont" id="mobile-nav">
        <div class="mobile-view-nav-head">
            <p>Menu</p>
        </div>
        <div class="mobile-view-nav-list">
            <ul>
                <li><a href="index.html" class="mobile-view-list">HOME</a></li>
                <li><a href="index.html#section-3" class="mobile-view-list">CHAT BOT</a></li>
                <li><a href="otherHTML/statistics.html" class="mobile-view-list">STATISTICS</a></li>
                <li><a href="index.html#footer" class="mobile-view-list">CONTACT</a></li>
                <li><a href="login.html" class="mobile-view-list">LOGIN</a></li>
            </ul>
        </div>
    </div>

    <div class="reset-container">
        <div class="reset-header">
            <h2 style="color: var(--dark-color);">Set New <span style="color: var(--primary-color);">Password</span></h2>
            <p style="color: var(--dark-color); font-size: 0.9rem;">Choose a strong password for your account</p>
        </div>

        <form method="POST" action="reset_password.php">
            <input type="hidden" name="token" value="<?= attr($token) ?>">

            <div class="form-group">
                <label for="password">New Password</label>
                <input type="password" id="password" name="password" required minlength="8" placeholder="At least 8 characters">
            </div>

            <div class="form-group">
                <label for="confirm_password">Confirm Password</label>
                <input type="password" id="confirm_password" name="confirm_password" required minlength="8" placeholder="Re-enter new password">
                <p class="error-message" id="error-msg"></p>
            </div>

            <button type="submit" class="reset-btn">Reset Password</button>
        </form>

        <div class="return-links">
            <p><a href="login.html">Back to Login</a></p>
        </div>
    </div>

    <script src="otherJS/hamberger.js"></script>
    <script>
        const urlParams = new URLSearchParams(window.location.search);
        const err = urlParams.get('error');
        if (err) {
            const errorEl = document.getElementById('error-msg');
            if (err === 'missing') errorEl.textContent = 'All fields are required.';
            else if (err === 'mismatch') errorEl.textContent = 'Passwords do not match.';
            else if (err === 'weak') errorEl.textContent = 'Password must be at least 8 characters.';
            else if (err === 'rate_limit') errorEl.textContent = 'Too many attempts. Please try again later.';
            else if (err === 'invalid_token') errorEl.textContent = 'This reset link is invalid or has expired.';
            errorEl.style.display = 'block';
        }

        fetch('csrf.php')
            .then(response => response.json())
            .then(data => {
                const forms = document.querySelectorAll('form');
                forms.forEach(form => {
                    const input = document.createElement('input');
                    input.type = 'hidden';
                    input.name = 'csrf_token';
                    input.value = data.csrf_token;
                    form.appendChild(input);
                });
            })
            .catch(error => console.error('Error fetching CSRF token:', error));
    </script>
    <script src="otherJS/accessibility.js"></script>
</body>
</html>
