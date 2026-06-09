(function() {
    var toggle = document.getElementById('theme-toggle');
    if (toggle) {
        var moonIcon = toggle.querySelector('.fa-moon');
        var sunIcon = toggle.querySelector('.fa-sun');
        function setTheme(dark) {
            if (dark) {
                document.documentElement.setAttribute('data-theme', 'dark');
                localStorage.setItem('theme', 'dark');
                if (moonIcon) moonIcon.style.display = 'none';
                if (sunIcon) sunIcon.style.display = 'inline-block';
            } else {
                document.documentElement.removeAttribute('data-theme');
                localStorage.setItem('theme', 'light');
                if (moonIcon) moonIcon.style.display = 'inline-block';
                if (sunIcon) sunIcon.style.display = 'none';
            }
        }
        
        // Initial setup based on localStorage
        if (localStorage.getItem('theme') === 'dark') {
            setTheme(true);
        } else {
            setTheme(false);
        }

        toggle.addEventListener('click', function() {
            var isDark = document.documentElement.getAttribute('data-theme') === 'dark';
            setTheme(!isDark);
        });
    }
})();
