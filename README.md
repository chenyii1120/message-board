# Message Board

這是可放進 XAMPP `htdocs/message-board/` 的 PHP + MySQL + jQuery 單頁留言板小專案。v1 範圍包含：留言列表、新增留言、基本輸入驗證、SQL Injection 防護與 XSS 防護。

## XAMPP 快速開始

最短流程如下：

1. 安裝 XAMPP，並在 XAMPP Control Panel 啟動 `Apache` 與 `MySQL`。
2. 將整個專案資料夾複製到 XAMPP 的 `htdocs/message-board/`：
   - Windows：`C:\xampp\htdocs\message-board\`
   - macOS：`/Applications/XAMPP/htdocs/message-board/`
   - Linux：`/opt/lampp/htdocs/message-board/`
3. 開啟 `http://localhost/phpmyadmin/`，匯入 `database/schema.sql`。
4. 開啟 `http://localhost/message-board/`，即可新增與查看留言。

如果頁面打得開但留言列表載入失敗，請優先確認：

- XAMPP 的 `MySQL` 是否已啟動。
- `database/schema.sql` 是否已成功建立 `message_board.messages`。
- `api/db.php` 的連線設定是否符合你的 MySQL host、port、帳號與密碼；預設是 XAMPP 常見的 `root` / 空密碼。

## 檔案

- `index.html`：單頁留言板 UI，包含暱稱輸入框、留言 textarea、回饋訊息與留言列表。
- `assets/js/app.js`：jQuery AJAX 互動；頁面載入呼叫 `api/list.php`，送出表單 POST 到 `api/create.php`，成功後清空內容並重新載入列表。
- `assets/css/styles.css`：簡潔卡片式留言列表與響應式排版。
- `api/db.php`：PDO 連線設定，預設連到 XAMPP 常見的 `127.0.0.1:3306`、資料庫 `message_board`、使用者 `root`、空密碼。
- `api/list.php`：取得最新留言，依 `created_at DESC, id DESC` 排序。
- `api/create.php`：新增留言，驗證暱稱與內容長度，使用 PDO prepared statements。
- `database/schema.sql`：建立資料庫與 `messages` 資料表。
- `tests/`：不需要 XAMPP 的靜態驗收測試，用來檢查 API、前端 escaping 與 README 交付文件。

## XAMPP 放置路徑

1. 安裝並啟動 XAMPP。
2. 將整個專案資料夾放到 XAMPP 的 `htdocs` 下，路徑建議為：
   - Windows：`C:\xampp\htdocs\message-board\`
   - macOS：`/Applications/XAMPP/htdocs/message-board/`
   - Linux：`/opt/lampp/htdocs/message-board/`
3. 確認瀏覽器可開啟：
   - `http://localhost/message-board/`

## 建立資料庫

### 方法 A：使用 phpMyAdmin

1. 開啟 XAMPP Control Panel，啟動 `Apache` 與 `MySQL`。
2. 在瀏覽器開啟 `http://localhost/phpmyadmin/`。
3. 匯入 `database/schema.sql`，或在 SQL 頁籤貼上該檔案內容後執行。
4. 預期會建立：
   - database：`message_board`
   - table：`messages`

### 方法 B：使用 mysql CLI

在專案根目錄執行：

```bash
mysql -u root < database/schema.sql
```

若你的 XAMPP root 有密碼：

```bash
mysql -u root -p < database/schema.sql
```

## 可調整的 DB 環境變數

若你的 XAMPP MySQL 不是預設值，可以在 Apache/PHP 環境設定：

- `MESSAGE_BOARD_DB_HOST`
- `MESSAGE_BOARD_DB_PORT`
- `MESSAGE_BOARD_DB_NAME`
- `MESSAGE_BOARD_DB_USER`
- `MESSAGE_BOARD_DB_PASSWORD`

預設值：

- host：`127.0.0.1`
- port：`3306`
- database：`message_board`
- user：`root`
- password：空字串

## 啟動方式與 URL

1. 啟動 XAMPP 的 `Apache` 與 `MySQL`。
2. 匯入 `database/schema.sql`。
3. 開啟：`http://localhost/message-board/`
4. 頁面載入時會呼叫：`http://localhost/message-board/api/list.php`
5. 送出留言時會 POST 到：`http://localhost/message-board/api/create.php`

## 從空資料庫開始的完整驗收流程

以下流程可以讓自己或他人在 XAMPP 本機從乾淨狀態重跑 v1。

### 1. 清空資料表

如果資料庫已存在，可以先清空 `messages`：

```sql
USE message_board;
TRUNCATE TABLE messages;
```

也可以直接重建整個資料庫：

```sql
DROP DATABASE IF EXISTS message_board;
SOURCE database/schema.sql;
```

如果使用 phpMyAdmin，請在 SQL 頁籤執行 `TRUNCATE TABLE messages;`，或重新匯入 `database/schema.sql`。

### 2. 確認空列表

```bash
curl http://localhost/message-board/api/list.php
```

預期回傳：

```json
{"success":true,"messages":[]}
```

### 3. 新增中文留言

```bash
curl -X POST http://localhost/message-board/api/create.php \
  -d "name=Joe" \
  -d "content=第一則中文留言"
```

預期回傳 HTTP `201`，JSON 內有 `success: true` 與剛新增的留言。

### 4. 新增英文留言

```bash
curl -X POST http://localhost/message-board/api/create.php \
  -d "name=Alice" \
  -d "content=Hello from English message"
```

### 5. 新增特殊符號留言

```bash
curl -X POST http://localhost/message-board/api/create.php \
  -d "name=Symbols" \
  -d "content=特殊符號 !@#$%^&*()_+-=[]{};':,./<>?"
```

### 6. 確認列表排序與資料

```bash
curl http://localhost/message-board/api/list.php
```

預期：

- `success: true`
- 至少有 3 筆留言。
- 最新留言在最上方，排序為 `created_at DESC, id DESC`。

## 安全性與輸入驗證驗收

### SQL Injection

`api/create.php` 使用 PDO prepared statements 與 `:name`、`:content` bind placeholders，不把使用者輸入直接串進 SQL。可以用以下 payload 確認它會被當成一般文字儲存，而不是破壞 SQL：

```bash
curl -X POST http://localhost/message-board/api/create.php \
  -d "name=' OR '1'='1" \
  -d "content=SQL Injection test'); DROP TABLE messages; --"
```

驗收重點：

- API 回傳 `success: true` 或正常驗證錯誤，但資料表不應被刪除。
- 再次呼叫 `api/list.php` 仍可正常讀取留言。

### XSS

前端 `assets/js/app.js` 在 render 留言前會用 jQuery `.text()` 產生 escaping 後的字串，再放進 HTML；因此 `<script>alert(1)</script>` 應該只會顯示成文字，不會執行。

測試 payload：

```bash
curl -X POST http://localhost/message-board/api/create.php \
  -d "name=XSS" \
  -d "content=<script>alert(1)</script>"
```

驗收重點：

- 重新整理 `http://localhost/message-board/`。
- 頁面不會跳出 alert。
- 留言列表中可以看到被轉義/顯示為文字的 `<script>alert(1)</script>`。

### 空欄位

```bash
curl -i -X POST http://localhost/message-board/api/create.php \
  -d "name=" \
  -d "content=有內容但沒有暱稱"

curl -i -X POST http://localhost/message-board/api/create.php \
  -d "name=Joe" \
  -d "content="
```

預期：

- HTTP `422`
- JSON：`success: false`
- `error` 顯示 `暱稱必填。` 或 `留言內容必填。`

### 超長欄位

暱稱最多 30 字，留言內容最多 500 字。超過限制時應回傳 HTTP `422` 與清楚錯誤訊息。

```bash
curl -i -X POST http://localhost/message-board/api/create.php \
  -d "name=abcdefghijklmnopqrstuvwxyz12345" \
  -d "content=正常內容"
```

預期 `暱稱最多 30 字。`

留言內容超長可在瀏覽器 textarea 貼上超過 500 字，或用腳本產生 POST。預期 `留言內容最多 500 字。`

## 本機靜態測試

這些測試不需要 PHP、MySQL 或 XAMPP，主要用來快速檢查 v1 專案結構、安全性實作痕跡與 README 是否足以重建專案：

```bash
python3 tests/test_api_static.py
python3 tests/test_frontend_static.py
python3 tests/test_readme_delivery.py
```

若三個指令都通過，表示：

- API 有 JSON response、PDO prepared statements、輸入驗證與錯誤格式。
- 前端會載入列表、AJAX 新增留言、避免重複送出、escape 使用者內容。
- README 有 XAMPP 放置路徑、資料庫 SQL、啟動 URL、從空資料庫開始的驗收流程、安全性測試與 v2 後續功能記錄。

## v1 驗收標準

- README 足以讓自己或他人在 XAMPP 本機重建專案。
- 從空資料庫開始，可以新增中文、英文、特殊符號留言並重新讀取列表。
- `<script>alert(1)</script>` 不會執行，只會以文字呈現。
- 空欄位與超長欄位會顯示錯誤，API 回傳 `success: false` 與 HTTP `422`。
- 基本安全風險已處理：
  - SQL Injection：使用 PDO prepared statements。
  - XSS：前端 render 前 escape 使用者輸入。
  - 輸入驗證：暱稱必填且最多 30 字；留言必填且最多 500 字。

## 後續 v2 可加功能

- 刪除留言：加入刪除按鈕、後端 delete API，並考慮 CSRF 防護。
- 編輯留言：加入 update API、編輯狀態 UI、updated_at 欄位。
- 分頁：列表 API 支援 `page` / `limit`，避免留言量變大後一次載入全部資料。
- 登入：加入使用者帳號，讓留言能綁定作者並限制刪除/編輯權限。
