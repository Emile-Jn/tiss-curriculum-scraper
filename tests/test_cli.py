import pandas as pd

from tiss_curriculum_scraper.cli import merge_curricula


def test_merge_curricula_prefers_current_active_row_when_full_module_name_changes():
    previous = pd.DataFrame(
        [
            {
                "module": "Foundations",
                "title": "Machine Learning",
                "code": "184.702",
                "type": "VU",
                "semester": "S",
                "credits": 4.5,
                "link": "https://example.com/old",
                "full_module_name": "Prüfungsfach Data Science - Foundations",
                "active": False,
            }
        ]
    )
    current = pd.DataFrame(
        [
            {
                "module": "Foundations",
                "title": "Machine Learning",
                "code": "184.702",
                "type": "VU",
                "semester": "S",
                "credits": 4.5,
                "link": "https://example.com/new",
                "full_module_name": "Modul MLS/FD - Machine Learning and Statistics - Foundations",
                "active": True,
            }
        ]
    )

    merged = merge_curricula(previous, current)

    assert merged.shape[0] == 1
    assert bool(merged.iloc[0]["active"]) is True
