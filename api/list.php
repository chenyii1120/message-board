<?php
declare(strict_types=1);

header('Content-Type: application/json; charset=utf-8');

try {
    require_once __DIR__ . '/db.php';

    $stmt = $pdo->query(
        'SELECT id, name, content, created_at
         FROM messages
         ORDER BY created_at DESC, id DESC'
    );

    echo json_encode([
        'success' => true,
        'messages' => $stmt->fetchAll(),
    ], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
} catch (Throwable $e) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'error' => '讀取留言失敗，請稍後再試。',
    ], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
}
