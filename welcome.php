<?php
require_once __DIR__ . '/session_config.php';
session_start();

if (!isset($_SESSION["username"])) {
    header("Location: login.html");
    exit();
}

if (empty($_SESSION['csrf_token'])) {
    $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome | PsycheCare</title>
    <link rel="stylesheet" href="style.css">
    <link rel="icon" href="Images/B_icon01.png">
    <script>
        if (localStorage.getItem('theme') === 'dark') {
            document.documentElement.setAttribute('data-theme', 'dark');
        }
    </script>
    <style>
        .welcome-wrap {
            min-height: 75vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 3rem 1.5rem;
        }

        .welcome-card {
            width: min(820px, 100%);
            background: var(--card-bg);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(127, 90, 240, 0.12);
            border-radius: 24px;
            box-shadow: 0 20px 60px rgba(127, 90, 240, 0.14);
            padding: 3rem 2rem;
            text-align: center;
            position: relative;
            overflow: hidden;
        }

        .welcome-card::before {
            content: "";
            position: absolute;
            inset: auto auto -90px -90px;
            width: 220px;
            height: 220px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(127, 90, 240, 0.18), rgba(127, 90, 240, 0));
        }

        .welcome-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.55rem 1rem;
            border-radius: 999px;
            background: rgba(127, 90, 240, 0.1);
            color: var(--primary-color);
            font-weight: 600;
            margin-bottom: 1.25rem;
        }

        .welcome-title {
            margin: 0;
            font-size: clamp(2rem, 4vw, 3.4rem);
            color: var(--dark-color);
            line-height: 1.1;
        }

        .welcome-title span {
            color: var(--primary-color);
        }

        .welcome-text {
            max-width: 620px;
            margin: 1rem auto 0;
            color: var(--dark-color);
            font-size: 1.05rem;
            line-height: 1.8;
        }

        .welcome-actions {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 1rem;
            margin-top: 2rem;
        }

        .welcome-note {
            margin-top: 1.5rem;
            color: var(--dark-color);
            font-size: 0.95rem;
            opacity: 0.85;
        }

        @media (max-width: 640px) {
            .welcome-card {
                padding: 2.2rem 1.25rem;
            }
        }
        
        .logout-form {
            display: inline;
        }
        
        .logout-btn {
            background: none;
            border: none;
            color: #fff;
            font-weight: 500;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-family: inherit;
            font-size: 1rem;
            text-transform: uppercase;
        }
        
        .logout-btn:hover {
            background: rgba(108, 92, 231, 0.2);
            transform: translateY(-2px);
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
                    <li><a href="otherHTML/chatBot.php">CHAT BOT</a></li>
                    <li><a href="otherHTML/statistics.html">STATISTICS</a></li>
                    <li><a href="contact.html">CONTACT</a></li>
                    <li>
                        <form method="POST" action="logout.php" class="logout-form">
                            <input type="hidden" name="csrf_token" value="<?php echo htmlspecialchars($_SESSION['csrf_token']); ?>">
                            <button type="submit" class="logout-btn">LOGOUT</button>
                        </form>
                    </li>
                </ul>
            </div>

            <button id="theme-toggle" class="theme-toggle-btn" aria-label="Toggle theme">
                <i class="fas fa-moon"></i>
                <i class="fas fa-sun" style="display:none"></i>
            </button>
        </div>
    </div>

    <div class="welcome-wrap">
        <div class="welcome-card">
            <div class="welcome-badge">Signed in successfully</div>
            <h1 class="welcome-title">Welcome, <span><?php echo htmlspecialchars($_SESSION["username"]); ?></span></h1>
            <p class="welcome-text">
                You are now inside PsycheCare. Explore the chatbot, browse wellness resources, and continue your
                mental health journey from one place.
            </p>
            <div class="welcome-actions">
                <a href="index.html"><button class="explore-btn">Go to Home</button></a>
                <a href="otherHTML/chatBot.php"><button class="blog-btn">Open Chat Bot</button></a>
            </div>
            <p class="welcome-note">If you were not expecting this page, simply return to the home screen.</p>
        </div>
    </div>
    <script src="otherJS/theme.js"></script>
</body>
</html>
