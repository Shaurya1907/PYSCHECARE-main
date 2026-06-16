<?php
/**
 * Centralized robust output escaping utility
 * Protects against Cross Site Scripting (XSS) across different rendering contexts.
 */

if (!defined('ENT_HTML5')) {
    define('ENT_HTML5', 48);
}

/**
 * Sanitize text for HTML body context.
 */
function sanitizeHTML($string) {
    if ($string === null) {
        return '';
    }
    return htmlspecialchars((string)$string, ENT_QUOTES | ENT_HTML5, 'UTF-8');
}

/**
 * Sanitize text for HTML attribute context.
 */
function sanitizeAttribute($string) {
    if ($string === null) {
        return '';
    }
    return htmlspecialchars((string)$string, ENT_QUOTES | ENT_HTML5, 'UTF-8');
}

/**
 * Sanitize data for JavaScript context (inside <script> tags).
 */
function sanitizeJS($data) {
    if ($data === null) {
        return 'null';
    }
    // Prevent XSS by converting special chars into unicode escapes
    return json_encode($data, JSON_HEX_TAG | JSON_HEX_APOS | JSON_HEX_QUOT | JSON_HEX_AMP | JSON_UNESCAPED_UNICODE);
}

/**
 * Sanitize URL to ensure it is safe and uses allowed protocols.
 */
function sanitizeURL($url) {
    if ($url === null) {
        return '';
    }
    $url = trim((string)$url);
    if (preg_match('/^(https?:\/\/|\/)/i', $url)) {
        return filter_var($url, FILTER_SANITIZE_URL);
    }
    return '/'; // fallback to safe relative root
}

/**
 * Short alias for HTML context escaping.
 */
function e($string) {
    return sanitizeHTML($string);
}

/**
 * Short alias for attribute context escaping.
 */
function attr($string) {
    return sanitizeAttribute($string);
}
?>
