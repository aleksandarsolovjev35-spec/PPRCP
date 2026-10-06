<?php
// Configure these values through environment variables in a real deployment.
$host = getenv('DB_HOST') ?: '127.0.0.1';
$port = getenv('DB_PORT') ?: '3306';
$name = getenv('DB_NAME') ?: 'anok_portal';
$user = getenv('DB_USER') ?: 'anok';
$pass = getenv('DB_PASSWORD') ?: 'anok_password';
$dsn = "mysql:host=$host;port=$port;dbname=$name;charset=utf8mb4";
try {
    $pdo = new PDO($dsn, $user, $pass, [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_EMULATE_PREPARES => false,
    ]);
} catch (PDOException $e) {
    http_response_code(500);
    exit('Не удалось подключиться к базе данных. Проверьте настройки DB_HOST, DB_NAME, DB_USER и DB_PASSWORD.');
}
