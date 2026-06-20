<?php
require_once __DIR__ . '/session_config.php';
session_start();

require_once __DIR__ . '/database.php';
require_once __DIR__ . '/validation.php';

header('Content-Type: application/json');

function jsonResponse(array $payload, int $code = 200): void
{
    http_response_code($code);
    echo json_encode($payload);
    exit();
}

function jsonError(string $message, string $error = 'validation', int $code = 400): void
{
    error_log(sprintf('[Medication] validation failure from %s: %s', getIPAddress(), $message));
    jsonResponse(['success' => false, 'error' => $error, 'message' => $message], $code);
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    jsonError('Invalid request method.', 'method', 405);
}

if (
    empty($_POST['csrf_token']) ||
    empty($_SESSION['csrf_token']) ||
    !hash_equals($_SESSION['csrf_token'], $_POST['csrf_token'])
) {
    jsonError('Invalid request token.', 'csrf', 403);
}

$medicationName = htmlspecialchars(trim((string) ($_POST['medication_name'] ?? '')), ENT_QUOTES, 'UTF-8');
$dosageAmountRaw = trim((string) ($_POST['dosage_amount'] ?? ''));
$dosageUnit = htmlspecialchars(trim((string) ($_POST['dosage_unit'] ?? '')), ENT_QUOTES, 'UTF-8');
$frequency = htmlspecialchars(trim((string) ($_POST['frequency'] ?? '')), ENT_QUOTES, 'UTF-8');
$startDateRaw = trim((string) ($_POST['start_date'] ?? ''));
$notes = htmlspecialchars(trim((string) ($_POST['notes'] ?? '')), ENT_QUOTES, 'UTF-8');

$allowedUnits = ['mg', 'mcg', 'ml', 'tablet', 'capsule', 'drop', 'puff'];
$allowedFrequencies = ['Once daily', 'Twice daily', 'Three times daily', 'Every 8 hours', 'As needed'];

if (!isRequired($medicationName) || strlen($medicationName) < 2 || strlen($medicationName) > 100) {
    jsonError('Medication name is required and must be 2–100 characters.');
}

if ($dosageAmountRaw === '' || !is_numeric($dosageAmountRaw)) {
    jsonError('Dosage must be a number between 0.1 and 1000');
}

$dosageAmount = (float) $dosageAmountRaw;
if ($dosageAmount < 0.1 || $dosageAmount > 1000) {
    jsonError('Dosage must be a number between 0.1 and 1000');
}

if (!in_array($dosageUnit, $allowedUnits, true)) {
    jsonError('Please select a valid unit (mg, ml, etc.)');
}

if (!in_array($frequency, $allowedFrequencies, true)) {
    jsonError('Please select a valid frequency.');
}

if ($startDateRaw === '' || !preg_match('/^\d{4}-\d{2}-\d{2}$/', $startDateRaw)) {
    jsonError('Please enter a valid start date.');
}

$startTimestamp = strtotime($startDateRaw);
if ($startTimestamp === false) {
    jsonError('Please enter a valid start date.');
}

$today = strtotime('today');
if ($startTimestamp > $today) {
    jsonError('Start date cannot be in the future');
}

if (!isMaxLength($notes, 500)) {
    jsonError('Notes must be 500 characters or less.');
}

try {
    $db = getAuthDatabase();
    $db->exec(
        "CREATE TABLE IF NOT EXISTS medications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            medication_name TEXT NOT NULL,
            dosage_amount REAL NOT NULL,
            dosage_unit TEXT NOT NULL,
            frequency TEXT NOT NULL,
            start_date DATE NOT NULL,
            notes TEXT DEFAULT '',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        )"
    );

    $stmt = $db->prepare(
        "INSERT INTO medications (user_id, medication_name, dosage_amount, dosage_unit, frequency, start_date, notes)
         VALUES (:user_id, :medication_name, :dosage_amount, :dosage_unit, :frequency, :start_date, :notes)"
    );

    $stmt->execute([
        ':user_id' => $_SESSION['user_id'] ?? null,
        ':medication_name' => $medicationName,
        ':dosage_amount' => $dosageAmount,
        ':dosage_unit' => $dosageUnit,
        ':frequency' => $frequency,
        ':start_date' => date('Y-m-d', $startTimestamp),
        ':notes' => $notes,
    ]);

    jsonResponse(['success' => true, 'message' => 'Medication saved! 🎉']);
} catch (PDOException $exception) {
    error_log(sprintf('[Medication] database error from %s: %s', getIPAddress(), $exception->getMessage()));
    jsonError('Unable to save medication at this time. Please try again later.', 'server', 500);
}
