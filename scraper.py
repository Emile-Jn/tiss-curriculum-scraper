#!/usr/bin/python3
"""Compatibility wrapper for the package entry point."""

from tiss_curriculum_scraper.cli import extract_and_save_all_courses, main
from tiss_curriculum_scraper.scraping import extract_ects, extract_ects_from_html

__all__ = [
    "extract_and_save_all_courses",
    "extract_ects",
    "extract_ects_from_html",
    "main",
]


if __name__ == "__main__":
    main()
