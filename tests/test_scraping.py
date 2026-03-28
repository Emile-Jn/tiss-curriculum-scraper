from pathlib import Path

import pytest

from scraper import extract_ects_from_html
from tiss_curriculum_scraper.scraping import build_course_row, normalize_text, parse_course_info


def test_parse_course_info_requires_three_parts():
    assert parse_course_info("188.995 VU 2024W") == ("188.995", "VU", "2024W")

    with pytest.raises(ValueError, match="Unexpected course key format"):
        parse_course_info("188.995")


def test_build_course_row_sanitizes_tabs_and_parses_values():
    row = build_course_row(
        "Data\tScience",
        "188.995 VU 2024W",
        "3.0",
        "https://example.com/course",
    )

    assert row == {
        "title": "Data Science",
        "code": "188.995",
        "type": "VU",
        "semester": "2024W",
        "credits": 3.0,
        "link": "https://example.com/course",
    }


def test_build_course_row_rejects_implausible_credits():
    with pytest.raises(ValueError, match="less than 0.5"):
        build_course_row("Course", "188.995 VU 2024W", "0.0", "https://example.com/course")


def test_extract_ects_from_fixture():
    html = Path("tests/fixtures/course_details.html").read_text(encoding="utf-8")

    assert extract_ects_from_html(html, "https://example.com/course") == 3.0


def test_normalize_text_handles_umlauts():
    assert normalize_text("Prüfungsfach Freie Wahlfächer") == "Prufungsfach Freie Wahlfacher"
