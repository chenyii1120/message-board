#!/usr/bin/env python3
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "api"


def read(name: str) -> str:
    return (API / name).read_text(encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_list_php_returns_json_and_orders_latest_messages():
    source = read("list.php")
    require("Content-Type: application/json" in source, "list.php must set JSON Content-Type")
    require(bool(re.search(r"ORDER\s+BY\s+created_at\s+DESC\s*,\s*id\s+DESC", source, re.I)), "list.php must order latest messages first")
    require("json_encode" in source, "list.php must encode JSON")
    require("require_once __DIR__ . '/db.php'" in source or 'require_once __DIR__ . "/db.php"' in source, "list.php must load db.php")


def test_create_php_validates_name_and_content_limits():
    source = read("create.php")
    require("Content-Type: application/json" in source, "create.php must set JSON Content-Type")
    require(bool(re.search(r"mb_strlen\s*\(\s*\$name\s*,\s*'UTF-8'\s*\)\s*>\s*30", source)), "create.php must limit name to 30 chars")
    require(bool(re.search(r"mb_strlen\s*\(\s*\$content\s*,\s*'UTF-8'\s*\)\s*>\s*500", source)), "create.php must limit content to 500 chars")
    require("暱稱必填" in source, "create.php must reject blank name")
    require("留言內容必填" in source, "create.php must reject blank content")
    require("暱稱最多 30 字" in source, "create.php must return clear name length error")
    require("留言內容最多 500 字" in source, "create.php must return clear content length error")


def test_create_php_uses_pdo_prepared_statement_for_insert():
    source = read("create.php")
    require("->prepare(" in source, "create.php must use PDO prepare")
    require(":name" in source, "create.php must bind :name")
    require(":content" in source, "create.php must bind :content")
    require(bool(re.search(r"INSERT\s+INTO\s+messages", source, re.I)), "create.php must insert into messages")
    require("lastInsertId" in source, "create.php should return/lookup the new row")


def test_php_api_has_clear_json_error_responses():
    combined = read("list.php") + "\n" + read("create.php")
    require("http_response_code" in combined, "API must set HTTP error codes")
    require(bool(re.search(r"json_encode\s*\(\s*\[\s*'success'\s*=>\s*false", combined)), "API must return success:false JSON errors")
    require("error" in combined, "API errors must include error key")


def test_db_php_configures_pdo_safely_for_xampp_mysql():
    source = read("db.php")
    require("PDO::ATTR_ERRMODE" in source, "db.php must set PDO errmode")
    require("PDO::ERRMODE_EXCEPTION" in source, "db.php must use exceptions")
    require("PDO::ATTR_DEFAULT_FETCH_MODE" in source, "db.php must set fetch mode")
    require("PDO::FETCH_ASSOC" in source, "db.php must fetch associative arrays")
    require("PDO::ATTR_EMULATE_PREPARES" in source, "db.php must configure emulated prepares")
    require("false" in source, "db.php must disable emulated prepares")
    require("utf8mb4" in source, "db.php must use utf8mb4")


def test_db_connection_errors_are_returned_as_json_and_validation_runs_first():
    list_source = read("list.php")
    create_source = read("create.php")
    require(list_source.find("try {") < list_source.find("require_once __DIR__ . '/db.php'"), "list.php must include db.php inside try so DB errors become JSON")
    require(create_source.find("留言內容最多 500 字") < create_source.find("require_once __DIR__ . '/db.php'"), "create.php must validate input before opening DB connection")


if __name__ == "__main__":
    tests = [name for name in sorted(globals()) if name.startswith("test_")]
    failures = 0
    for name in tests:
        try:
            globals()[name]()
            print(f"PASS {name}")
        except Exception as exc:
            failures += 1
            print(f"FAIL {name}: {exc}")
    if failures:
        print(f"{failures} failed, {len(tests)-failures} passed")
        sys.exit(1)
    print(f"{len(tests)} passed")
