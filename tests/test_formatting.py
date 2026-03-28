import pandas as pd
import pytest

from tiss_curriculum_scraper.formatting import (
    merge_years,
    modified_courses,
    remove_canceled_courses,
    remove_year_info,
)


def test_remove_year_info_normalizes_semesters():
    assert remove_year_info("2024W") == "W"
    assert remove_year_info("2025S") == "S"
    assert remove_year_info("2024W 2025S") == "W and S"
    assert remove_year_info("") == ""


def test_merge_years_returns_copy_with_normalized_semesters():
    original = pd.DataFrame({"semester": ["2024W", "2025S"]})

    result = merge_years(original)

    assert result["semester"].tolist() == ["W", "S"]
    assert original["semester"].tolist() == ["2024W", "2025S"]


def test_remove_canceled_courses_ignores_missing_titles():
    dataframe = pd.DataFrame(
        {
            "title": ["Useful Course", "Canceled by department", None],
            "semester": ["W", "S", "W"],
        }
    )

    result = remove_canceled_courses(dataframe)

    assert result["title"].iloc[0] == "Useful Course"
    assert pd.isna(result["title"].iloc[1])


def test_modified_courses_detects_added_and_removed_rows():
    old_df = pd.DataFrame(
        [
            {
                "module": "Foundations",
                "title": "Existing",
                "code": "123.456",
                "type": "VO",
                "semester": "W",
                "credits": 3.0,
                "link": "https://example.com/old",
                "full_module_name": "Foundations Full",
                "active": True,
            },
            {
                "module": "TSK",
                "title": "Removed",
                "code": "111.111",
                "type": "UE",
                "semester": "S",
                "credits": 2.0,
                "link": "https://example.com/removed",
                "full_module_name": "TSK Full",
                "active": True,
            },
        ]
    )
    new_df = pd.DataFrame(
        [
            {
                "module": "Foundations",
                "title": "Existing",
                "code": "123.456",
                "type": "VO",
                "semester": "W",
                "credits": 3.0,
                "link": "https://example.com/new-link",
                "full_module_name": "Foundations Full",
                "active": True,
            },
            {
                "module": "TSK",
                "title": "Removed",
                "code": "111.111",
                "type": "UE",
                "semester": "S",
                "credits": 2.0,
                "link": "https://example.com/removed",
                "full_module_name": "TSK Full",
                "active": False,
            },
            {
                "module": "DSA",
                "title": "Added",
                "code": "222.222",
                "type": "SE",
                "semester": "S",
                "credits": 4.0,
                "link": "https://example.com/added",
                "full_module_name": "DSA Full",
                "active": True,
            },
        ]
    )

    added, removed = modified_courses(old_df, new_df)

    assert added["title"].tolist() == ["Added"]
    assert removed["title"].tolist() == ["Removed"]


def test_modified_courses_rejects_orphan_inactive_rows():
    old_df = pd.DataFrame(
        [
            {
                "module": "TSK",
                "title": "Historical",
                "code": "111.111",
                "type": "UE",
                "semester": "S",
                "credits": 2.0,
                "link": "https://example.com/historical",
                "full_module_name": "TSK Full",
                "active": False,
            }
        ]
    )
    new_df = pd.DataFrame(columns=old_df.columns)

    with pytest.raises(ValueError, match="inactive courses in old_df"):
        modified_courses(old_df, new_df)
