// Dark Mode Toggle Script

// ── Early apply (runs before first paint) ───────────────────────────────────
(() => {
    const saved = localStorage.getItem('darkMode');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    if (saved === 'enabled' || (saved === null && prefersDark)) {
        document.documentElement.classList.add('dark-mode');
    }
})();

// ── Interactive toggle (wired after DOM is ready) ───────────────────────────
document.addEventListener('DOMContentLoaded', function () {
    const darkModeToggle = document.getElementById('darkModeToggle');
    const body = document.body;

    // Sync body class with the early-applied html class
    const isDarkMode = document.documentElement.classList.contains('dark-mode');
    if (isDarkMode) {
        body.classList.add('dark-mode');
        if (darkModeToggle) {
            darkModeToggle.innerHTML = '<i class="fas fa-sun"></i>';
            darkModeToggle.setAttribute('title', 'Toggle Light Mode');
            darkModeToggle.setAttribute('aria-label', 'Toggle Light Mode');
        }
    }

    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function () {
            body.classList.toggle('dark-mode');
            document.documentElement.classList.toggle('dark-mode');

            if (body.classList.contains('dark-mode')) {
                localStorage.setItem('darkMode', 'enabled');
                darkModeToggle.innerHTML = '<i class="fas fa-sun"></i>';
                darkModeToggle.setAttribute('title', 'Toggle Light Mode');
                darkModeToggle.setAttribute('aria-label', 'Toggle Light Mode');
            } else {
                localStorage.setItem('darkMode', 'disabled');
                darkModeToggle.innerHTML = '<i class="fas fa-moon"></i>';
                darkModeToggle.setAttribute('title', 'Toggle Dark Mode');
                darkModeToggle.setAttribute('aria-label', 'Toggle Dark Mode');
            }
        });
    }
});