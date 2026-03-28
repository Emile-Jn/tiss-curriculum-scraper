from urllib.request import urlopen

from scraper import extract_ects

EXAMPLE_URL = "https://tiss.tuwien.ac.at/course/courseDetails.xhtml?dswid=9085&dsrid=196&semester=2026S&courseNr=163182"

def test_example_url_returns_html_page():
    with urlopen(EXAMPLE_URL) as response:
        html = response.read().decode("utf-8", errors="replace")

    assert "<html" in html.lower()
    assert "<title>" in html.lower()


def test_extract_ects_returns_reasonable_value_for_example_url():
    ects = extract_ects(EXAMPLE_URL)

    assert 0 < ects < 30
