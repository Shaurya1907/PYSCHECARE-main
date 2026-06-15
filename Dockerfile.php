FROM php:8.2-apache

# Install dependencies for SQLite
RUN apt-get update && apt-get install -y \
    sqlite3 \
    libsqlite3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Enable PDO SQLite extension
RUN docker-php-ext-install pdo pdo_sqlite

# Enable Apache mod_rewrite for nice URLs if needed
RUN a2enmod rewrite

# Copy application files
COPY . /var/www/html/

# Set permissions and create non-root user
RUN chown -R www-data:www-data /var/www/html
USER www-data

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/ || exit 1
