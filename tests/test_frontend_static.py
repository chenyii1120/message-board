#!/usr/bin/env python3
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
CSS = ROOT / "assets" / "css" / "styles.css"
JS = ROOT / "assets" / "js" / "app.js"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_index_html_contains_required_message_board_elements_and_assets():
    source = read(INDEX)
    require('<input' in source and 'id="name"' in source and 'name="name"' in source, "index.html must include a nickname input")
    require('<textarea' in source and 'id="content"' in source and 'name="content"' in source, "index.html must include a message textarea")
    require('id="submit-button"' in source and 'type="submit"' in source, "index.html must include a submit button")
    require('id="feedback"' in source, "index.html must include a feedback area")
    require('id="message-list"' in source, "index.html must include a message list area")
    require('jquery' in source.lower(), "index.html must load jQuery")
    require('assets/css/styles.css' in source, "index.html must load the stylesheet")
    require('assets/js/app.js' in source, "index.html must load the app script")


def test_app_js_loads_messages_on_page_ready_from_list_api():
    source = read(JS)
    require(bool(re.search(r"\$\s*\(\s*(?:document)?\s*\)\s*\.ready|\$\s*\(\s*function", source)), "app.js must run on page ready")
    require('api/list.php' in source, "app.js must call api/list.php")
    require(bool(re.search(r"function\s+loadMessages|const\s+loadMessages|let\s+loadMessages", source)), "app.js must define a loadMessages function")
    require(bool(re.search(r"loadMessages\s*\(\s*\)", source)), "app.js must call loadMessages on initial load")


def test_app_js_posts_form_with_ajax_and_prevents_duplicate_submits():
    source = read(JS)
    require('api/create.php' in source, "app.js must post to api/create.php")
    require(bool(re.search(r"\.on\s*\(\s*['\"]submit['\"]", source)), "app.js must handle form submit")
    require(bool(re.search(r"method\s*:\s*['\"]POST['\"]|type\s*:\s*['\"]POST['\"]", source)), "app.js must use POST")
    require(bool(re.search(r"submit-button|\$submit", source)), "app.js must target the submit button")
    require("prop('disabled', isSubmitting)" in source or 'prop("disabled", isSubmitting)' in source or bool(re.search(r"prop\s*\(\s*['\"]disabled['\"]\s*,\s*true", source)), "app.js must disable the button while submitting")
    require("setSubmitting(true)" in source, "app.js must enter submitting state before POST")
    require("setSubmitting(false)" in source or bool(re.search(r"prop\s*\(\s*['\"]disabled['\"]\s*,\s*false", source)), "app.js must re-enable the button after submit")
    require(bool(re.search(r"content\s*\.val\s*\(\s*['\"]{0,1}\s*['\"]{0,1}\s*\)|\$content\.val\s*\(\s*['\"]\s*['\"]\s*\)", source)), "app.js must clear message content after successful create")


def test_app_js_escapes_user_content_before_rendering_messages():
    source = read(JS)
    require(bool(re.search(r"function\s+escapeHtml|const\s+escapeHtml|let\s+escapeHtml", source)), "app.js must define an escapeHtml helper")
    require('.text(' in source, "escapeHtml should use jQuery .text() or equivalent safe escaping")
    require(bool(re.search(r"escapeHtml\s*\(\s*message\.name|escapeHtml\s*\(\s*item\.name", source)), "message names must be escaped before rendering")
    require(bool(re.search(r"escapeHtml\s*\(\s*message\.content|escapeHtml\s*\(\s*item\.content", source)), "message contents must be escaped before rendering")
    require(".html(response" not in source and ".html(data" not in source, "app.js must not inject raw API response HTML")


def test_css_defines_clean_card_style_message_list():
    source = read(CSS)
    require('.message-card' in source, "CSS must define message-card styling")
    require('border-radius' in source, "cards should have rounded corners")
    require('box-shadow' in source, "cards should use subtle shadow")
    require('max-width' in source, "layout should constrain width for readability")
    require('@media' in source, "CSS should include a small responsive adjustment")


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
