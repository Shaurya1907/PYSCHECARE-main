<?php

const MAX_USERNAME_LENGTH = 50;
const MAX_EMAIL_LENGTH = 254;
const MAX_NAME_LENGTH = 100;
const MAX_MESSAGE_LENGTH = 1000;
const MIN_PASSWORD_LENGTH = 8;

function isRequired(?string $value): bool
{
    return trim((string) $value) !== '';
}

function isMaxLength(?string $value, int $max): bool
{
    return strlen((string) $value) <= $max;
}

function isValidEmailInput(?string $email): bool
{
    $email = trim((string) $email);
    return isRequired($email)
        && isMaxLength($email, MAX_EMAIL_LENGTH)
        && filter_var($email, FILTER_VALIDATE_EMAIL) !== false;
}

function isValidUsername(?string $username): bool
{
    $username = trim((string) $username);
    return isRequired($username)
        && isMaxLength($username, MAX_USERNAME_LENGTH)
        && preg_match('/^[A-Za-z0-9_.-]+$/', $username) === 1;
}

function isValidPassword(?string $password): bool
{
    $pwd = (string) $password;
    if (strlen($pwd) < MIN_PASSWORD_LENGTH) return false;
    if (!preg_match('/[A-Z]/', $pwd)) return false;
    if (!preg_match('/[a-z]/', $pwd)) return false;
    if (!preg_match('/[0-9]/', $pwd)) return false;
    if (!preg_match('/[^a-zA-Z0-9]/', $pwd)) return false;
    
    return true;
}

function isValidMessage(?string $message): bool
{
    $message = trim((string) $message);
    return isRequired($message) && isMaxLength($message, MAX_MESSAGE_LENGTH);
}

function validateSignupInput(string $username, string $email, string $password): ?string
{
    if (!isValidUsername($username)) {
        return 'username';
    }
    if (!isValidEmailInput($email)) {
        return 'email';
    }
    if (!isValidPassword($password)) {
        return 'weak_password';
    }
    return null;
}

function validateContactInput(string $name, string $email, string $message): ?string
{
    if (!isRequired($name) || !isMaxLength($name, MAX_NAME_LENGTH)) {
        return 'Please enter your name.';
    }
    if (!isValidEmailInput($email)) {
        return 'Please enter a valid email address.';
    }
    if (!isValidMessage($message)) {
        return 'Please enter a message under ' . MAX_MESSAGE_LENGTH . ' characters.';
    }
    return null;
}
