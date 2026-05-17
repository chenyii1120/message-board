<?php
declare(strict_types=1);

$host = getenv('MESSAGE_BOARD_DB_HOST') ?: '127.0.0.1';
$port = getenv('MESSAGE_BOARD_DB_PORT') ?: '3306';
$dbname = getenv('MESSAGE_BOARD_DB_NAME') ?: 'message_board';
$username = getenv('MESSAGE_BOARD_DB_USER') ?: 'root';
$password = getenv('MESSAGE_BOARD_DB_PASSWORD') ?: '';
$charset = 'utf8mb4';

$dsn = "mysql:host={$host};port={$port};dbname={$dbname};charset={$charset}";

$options = [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    PDO::ATTR_EMULATE_PREPARES => false,
];

$pdo = new PDO($dsn, $username, $password, $options);
