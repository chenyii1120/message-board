#!/usr/bin/env python3
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"


def readme() -> str:
    return README.read_text(encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_readme_documents_xampp_install_database_start_and_url():
    source = readme()
    require("htdocs/message-board" in source, "README must document the XAMPP htdocs/message-board path")
    require("database/schema.sql" in source, "README must point to the database SQL file")
    require("phpMyAdmin" in source or "mysql" in source.lower(), "README must explain how to import/run SQL")
    require("Apache" in source and "MySQL" in source, "README must explain starting Apache and MySQL")
    require("http://localhost/message-board/" in source, "README must document the local browser URL")


def test_readme_contains_reproducible_acceptance_flow_from_empty_database():
    source = readme()
    require("從空資料庫開始" in source, "README must include an empty-database acceptance section")
    require("TRUNCATE TABLE messages" in source or "DROP DATABASE" in source, "README must show how to reset to an empty messages table")
    require("curl" in source and "api/create.php" in source and "api/list.php" in source, "README must include API curl verification commands")
    require("中文" in source and "English" in source, "README must cover Chinese and English test messages")
    require("特殊符號" in source, "README must cover special-symbol messages")


def test_readme_documents_security_and_validation_checks():
    source = readme()
    require("SQL Injection" in source, "README must state SQL Injection protection")
    require("XSS" in source, "README must state XSS protection")
    require("<script>alert(1)</script>" in source, "README must include the script-tag XSS test payload")
    require("不會執行" in source or "不應執行" in source, "README must state that the script payload must not execute")
    require("空欄位" in source, "README must include blank-field validation")
    require("超長" in source, "README must include over-length validation")
    require("422" in source, "README must document validation HTTP 422 responses")


def test_readme_records_v2_follow_up_features():
    source = readme()
    for feature in ["刪除", "編輯", "分頁", "登入"]:
        require(feature in source, f"README must record v2 follow-up feature: {feature}")


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
