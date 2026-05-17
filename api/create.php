<?php
declare(strict_types=1);

header('Content-Type: application/json; charset=utf-8');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode([
        'success' => false,
        'error' => '只接受 POST 請求。',
    ], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    exit;
}

$name = trim((string)($_POST['name'] ?? ''));
$content = trim((string)($_POST['content'] ?? ''));

if ($name === '') {
    http_response_code(422);
    echo json_encode([
        'success' => false,
        'error' => '暱稱必填。',
    ], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    exit;
}

if (mb_strlen($name, 'UTF-8') > 30) {
    http_response_code(422);
    echo json_encode([
        'success' => false,
        'error' => '暱稱最多 30 字。',
    ], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    exit;
}

if ($content === '') {
    http_response_code(422);
    echo json_encode([
        'success' => false,
        'error' => '留言內容必填。',
    ], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    exit;
}

if (mb_strlen($content, 'UTF-8') > 500) {
    http_response_code(422);
    echo json_encode([
        'success' => false,
        'error' => '留言內容最多 500 字。',
    ], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    exit;
}

try {
    require_once __DIR__ . '/db.php';

    $stmt = $pdo->prepare(
        'INSERT INTO messages (name, content, created_at)
         VALUES (:name, :content, NOW())'
    );
    $stmt->execute([
        ':name' => $name,
        ':content' => $content,
    ]);

    $id = (int)$pdo->lastInsertId();
    $stmt = $pdo->prepare(
        'SELECT id, name, content, created_at
         FROM messages
         WHERE id = :id'
    );
    $stmt->execute([':id' => $id]);
    $message = $stmt->fetch();

    http_response_code(201);
    echo json_encode([
        'success' => true,
        'message' => $message,
    ], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
} catch (Throwable $e) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'error' => '新增留言失敗，請稍後再試。',
    ], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
}
