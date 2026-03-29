from pathlib import Path

import pytest
from selenium.webdriver.common.by import By

from scraper import extract_ects_from_html
from tiss_curriculum_scraper.constants import SECTION_NAMES
from tiss_curriculum_scraper.scraping import (
    build_course_row,
    create_empty_curriculum,
    normalize_text,
    parse_course_info,
    scrape_rows,
)


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


class FakeLink:
    def __init__(self, href: str):
        self.href = href

    def get_attribute(self, name: str):
        if name == "href":
            return self.href
        return None


class FakeCell:
    def __init__(self, text: str = "", title: str | None = None, course_key: str | None = None):
        self.text = text
        self._title = title
        self._course_key = course_key

    def find_element(self, by, value):
        if by == By.CLASS_NAME and value == "courseTitle":
            return FakeCell(text=self._title or "")
        if by == By.CLASS_NAME and value == "courseKey":
            return FakeCell(text=self._course_key or "")
        raise ValueError(f"Unsupported selector: {by}={value}")


class FakeRow:
    def __init__(self, cells, href: str | None = None):
        self._cells = cells
        self._href = href

    def find_elements(self, by, value):
        if by == By.TAG_NAME and value == "td":
            return self._cells
        if by == By.TAG_NAME and value == "a":
            return [FakeLink(self._href)] if self._href else []
        return []


def test_scrape_rows_stops_before_transferable_skills_section():
    rows = [
        FakeRow([FakeCell("Master programme Data Science"), FakeCell(), FakeCell(), FakeCell("120.0")]),
        FakeRow([FakeCell("Prüfungsfach Data Science - Foundations"), FakeCell(), FakeCell(), FakeCell("36.0")]),
        FakeRow(
            [
                FakeCell(
                    "105.731 VU 2026S / AKSTA Statistical Computing",
                    title="AKSTA Statistical Computing",
                    course_key="105.731 VU 2026S",
                ),
                FakeCell(),
                FakeCell("2.0"),
                FakeCell("3.0"),
            ],
            href="https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=105731&semester=2026S",
        ),
        FakeRow(
            [
                FakeCell("Prüfungsfach Freie Wahlfächer und Transferable Skills"),
                FakeCell(),
                FakeCell(),
                FakeCell("15.0"),
            ]
        ),
        FakeRow(
            [
                FakeCell(
                    "163.182 SE Technical English Presentation A",
                    title="Technical English Presentation A",
                    course_key="163.182 SE 2026S",
                ),
                FakeCell(),
                FakeCell("2.0"),
                FakeCell("2.0"),
            ],
            href="https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=163182&semester=2026S",
        ),
    ]

    result = scrape_rows(rows, create_empty_curriculum(True), SECTION_NAMES)

    assert result["title"].tolist() == ["AKSTA Statistical Computing"]
    assert result["module"].tolist() == ["Foundations"]
