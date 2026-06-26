<?php
require_once __DIR__ . '/../session_config.php';
require_once __DIR__ . '/../sanitize.php';
session_start();

require_once __DIR__ . '/../database.php';

// Strict session check
if (!isset($_SESSION["username"]) || !isset($_SESSION["user_id"])) {
    header("Location: ../login.html");
    exit();
}

$db = getAuthDatabase();
$userId = (int)$_SESSION["user_id"];

// Handle Journal Creation
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action']) && $_POST['action'] === 'create') {
    if (empty($_POST['csrf_token']) || !hash_equals($_SESSION['csrf_token'], $_POST['csrf_token'])) {
        die("CSRF token validation failed");
    }
    
    $title = trim($_POST['title'] ?? '');
    $content = trim($_POST['content'] ?? '');
    
    if (!empty($title) && !empty($content)) {
        $stmt = $db->prepare("INSERT INTO journals (user_id, title, content) VALUES (:user_id, :title, :content)");
        $stmt->execute([
            ':user_id' => $userId,
            ':title' => $title,
            ':content' => $content
        ]);
        header("Location: journal.php");
        exit();
    }
}

// Pagination logic
$limit = isset($_GET['limit']) ? (int)$_GET['limit'] : 20;
$page = isset($_GET['page']) ? (int)$_GET['page'] : 1;
if ($page < 1) $page = 1;
if ($limit < 1 || $limit > 100) $limit = 20;

$offset = ($page - 1) * $limit;

// Get total count
$countStmt = $db->prepare("SELECT COUNT(*) as total FROM journals WHERE user_id = :user_id");
$countStmt->execute([':user_id' => $userId]);
$totalItems = $countStmt->fetch()['total'];
$totalPages = ceil($totalItems / $limit);
if ($totalPages == 0) $totalPages = 1;

// Fetch journals for current page
$stmt = $db->prepare("SELECT id, title, content, created_at FROM journals WHERE user_id = :user_id ORDER BY created_at DESC LIMIT :limit OFFSET :offset");
$stmt->bindValue(':user_id', $userId, PDO::PARAM_INT);
$stmt->bindValue(':limit', $limit, PDO::PARAM_INT);
$stmt->bindValue(':offset', $offset, PDO::PARAM_INT);
$stmt->execute();
$journals = $stmt->fetchAll(PDO::FETCH_ASSOC);

if (isset($_GET['action']) && $_GET['action'] === 'fetch') {
    header('Content-Type: application/json');
    echo json_encode([
        'data' => $journals,
        'meta' => [
            'currentPage' => $page,
            'pageSize' => $limit,
            'totalItems' => $totalItems,
            'totalPages' => $totalPages,
            'hasNextPage' => $page < $totalPages
        ]
    ]);
    exit();
}

?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Journal | PsycheCare</title>
    <link rel="stylesheet" href="../style.css">
    <link rel="icon" href="../Images/B_icon01.png">
    <style>
        .journal-wrap {
            max-width: 800px;
            margin: 100px auto;
            padding: 2rem;
            background: rgba(255, 255, 255, 0.9);
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .journal-form {
            display: flex;
            flex-direction: column;
            gap: 1rem;
            margin-bottom: 2rem;
            background: #f9f9ff;
            padding: 1.5rem;
            border-radius: 8px;
            border: 1px solid rgba(127, 90, 240, 0.2);
        }
        .journal-form input, .journal-form textarea {
            width: 100%;
            padding: 0.8rem;
            border: 1px solid #ccc;
            border-radius: 6px;
            font-family: inherit;
        }
        .journal-form button {
            background: var(--primary-color, #7f5af0);
            color: white;
            border: none;
            padding: 0.8rem 1.5rem;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
            align-self: flex-start;
        }
        .journal-entry {
            border-bottom: 1px solid #eee;
            padding: 1.5rem 0;
        }
        .journal-entry:last-child {
            border-bottom: none;
        }
        .journal-title {
            margin: 0 0 0.5rem 0;
            color: #2b2c34;
        }
        .journal-date {
            font-size: 0.85rem;
            color: #94a1b2;
            margin-bottom: 1rem;
        }
        .journal-content {
            white-space: pre-wrap;
            color: #444;
            line-height: 1.6;
        }
        .pagination {
            display: flex;
            justify-content: center;
            gap: 1rem;
            margin-top: 2rem;
            align-items: center;
        }
        .pagination a, .pagination span {
            padding: 0.5rem 1rem;
            background: #fff;
            border: 1px solid #ccc;
            border-radius: 4px;
            text-decoration: none;
            color: #333;
        }
        .pagination a:hover {
            background: #eee;
        }
        .pagination .active {
            background: var(--primary-color, #7f5af0);
            color: white;
            border-color: var(--primary-color, #7f5af0);
        }
        .empty-state {
            text-align: center;
            padding: 3rem;
            color: #666;
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
                    <li><a href="../index.html">HOME</a></li>
                    <li><a href="chatBot.php">CHAT BOT</a></li>
                    <li><a href="journal.php">JOURNAL</a></li>
                    <li><a href="../welcome.php">DASHBOARD</a></li>
                </ul>
            </div>
        </div>
    </div>

    <div class="journal-wrap">
        <h2>My Journal</h2>
        
        <form class="journal-form" method="POST" action="journal.php">
            <input type="hidden" name="action" value="create">
            <input type="hidden" name="csrf_token" value="<?php echo attr($_SESSION['csrf_token']); ?>">
            <input type="text" name="title" placeholder="Journal Title" required>
            <textarea name="content" rows="4" placeholder="Write your thoughts..." required></textarea>
            <button type="submit">Save Entry</button>
        </form>

        <div class="journals-list" id="journalsList">
            <?php if (empty($journals)): ?>
                <div class="empty-state">
                    <h3>No journal entries yet</h3>
                    <p>Start writing your thoughts above.</p>
                </div>
            <?php else: ?>
                <?php foreach ($journals as $journal): ?>
                    <div class="journal-entry">
                        <h3 class="journal-title"><?php echo e($journal['title']); ?></h3>
                        <div class="journal-date"><?php echo e($journal['created_at']); ?></div>
                        <div class="journal-content"><?php echo nl2br(e($journal['content'])); ?></div>
                    </div>
                <?php endforeach; ?>
            <?php endif; ?>
        </div>

        <?php if ($totalPages > 1): ?>
        <div class="pagination" id="paginationContainer">
            <?php if ($page < $totalPages): ?>
                <button id="loadMoreJournalsBtn" data-page="<?php echo $page + 1; ?>" style="background: var(--primary-color, #7f5af0); color: white; border: none; padding: 0.8rem 1.5rem; border-radius: 6px; cursor: pointer; font-weight: bold;">Load More</button>
            <?php endif; ?>
        </div>
        <?php endif; ?>
    </div>

    <script>
        document.addEventListener("DOMContentLoaded", function() {
            const loadMoreBtn = document.getElementById("loadMoreJournalsBtn");
            const journalsList = document.getElementById("journalsList");

            if (loadMoreBtn) {
                loadMoreBtn.addEventListener("click", async function() {
                    const page = parseInt(this.getAttribute("data-page"));
                    const limit = <?php echo $limit; ?>;
                    
                    const originalText = this.innerText;
                    this.innerText = "Loading...";
                    this.disabled = true;

                    try {
                        const response = await fetch(`journal.php?action=fetch&page=${page}&limit=${limit}`);
                        if (!response.ok) throw new Error("Failed to fetch journals");
                        const result = await response.json();
                        
                        if (result.data && result.data.length > 0) {
                            result.data.forEach(journal => {
                                const entryDiv = document.createElement("div");
                                entryDiv.className = "journal-entry";
                                
                                const titleEl = document.createElement("h3");
                                titleEl.className = "journal-title";
                                titleEl.textContent = journal.title;
                                
                                const dateEl = document.createElement("div");
                                dateEl.className = "journal-date";
                                dateEl.textContent = journal.created_at;
                                
                                const contentEl = document.createElement("div");
                                contentEl.className = "journal-content";
                                contentEl.innerHTML = escapeHtml(journal.content).replace(/\\n/g, "<br>");
                                
                                entryDiv.appendChild(titleEl);
                                entryDiv.appendChild(dateEl);
                                entryDiv.appendChild(contentEl);
                                
                                journalsList.appendChild(entryDiv);
                            });

                            if (result.meta.hasNextPage) {
                                this.setAttribute("data-page", page + 1);
                                this.innerText = originalText;
                                this.disabled = false;
                            } else {
                                this.remove();
                            }
                        }
                    } catch (error) {
                        console.error(error);
                        this.innerText = originalText;
                        this.disabled = false;
                        alert("Failed to load more journals.");
                    }
                });
            }
            
            function escapeHtml(unsafe) {
                return unsafe
                     .replace(/&/g, "&amp;")
                     .replace(/</g, "&lt;")
                     .replace(/>/g, "&gt;")
                     .replace(/"/g, "&quot;")
                     .replace(/'/g, "&#039;");
            }
        });
    </script>
</body>
</html>
