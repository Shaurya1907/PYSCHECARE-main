(function() {
    fetch('csrf.php')
        .then(function(response) { return response.json(); })
        .then(function(data) {
            var forms = document.querySelectorAll('form');
            forms.forEach(function(form) {
                var input = document.createElement('input');
                input.type = 'hidden';
                input.name = 'csrf_token';
                input.value = data.csrf_token;
                form.appendChild(input);
            });
        })
        .catch(function(error) {
            console.error('Error fetching CSRF token:', error);
        });
})();
