FROM php:8.2-apache

# Install dependencies for SQLite
RUN apt-get update && apt-get install -y \
    sqlite3 \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# Enable PDO SQLite extension
RUN docker-php-ext-install pdo pdo_sqlite

# Enable Apache mod_rewrite for nice URLs if needed
RUN a2enmod rewrite

# Copy application files
COPY . /var/www/html/

# Set permissions
RUN chown -R www-data:www-data /var/www/html
