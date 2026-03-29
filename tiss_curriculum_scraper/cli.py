from __future__ import annotations

import logging

import pandas as pd

from .browser import initiate_chrome_driver
from .constants import CURRICULUM_PATH, DUPL_COLS, LOGS_PATH
from .formatting import modified_courses, normalize_output_module_names
from .scraping import clean_curriculum, get_data_science_curriculum, get_tsk_courses
from .storage import load_curriculum, log_changes, save_curriculum


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")


def merge_curricula(
    previous_curriculum: pd.DataFrame, current_curriculum: pd.DataFrame
) -> pd.DataFrame:
    """Merge old and new snapshots while preserving the latest active state per course."""
    identity_columns = current_curriculum.columns.difference(
        DUPL_COLS + ["active", "full_module_name"]
    )
    all_courses = pd.concat([previous_curriculum, current_curriculum], ignore_index=True)
    return all_courses.drop_duplicates(subset=identity_columns, keep="last").reset_index(
        drop=True
    )


def extract_and_save_all_courses() -> pd.DataFrame:
    previous_curriculum = load_curriculum(CURRICULUM_PATH)
    previous_curriculum["active"] = False

    driver = initiate_chrome_driver()
    try:
        curriculum, driver = get_data_science_curriculum(driver)
        if curriculum.shape[0] < 50:
            raise ValueError(
                "Scraping the Data Science curriculum failed, fewer than 50 courses found."
            )

        tsk_courses, driver = get_tsk_courses(driver)
        if tsk_courses.shape[0] < 50:
            raise ValueError("Scraping the TSK curriculum failed, fewer than 50 courses found.")
    finally:
        driver.quit()

    current_curriculum = pd.concat([curriculum, tsk_courses], ignore_index=True)
    current_curriculum = clean_curriculum(current_curriculum, DUPL_COLS)
    current_curriculum = normalize_output_module_names(current_curriculum)
    current_curriculum["active"] = True

    all_courses = merge_curricula(previous_curriculum, current_curriculum)
    save_curriculum(all_courses, CURRICULUM_PATH)
    return all_courses


def main() -> None:
    configure_logging()
    previous_curriculum = load_curriculum(CURRICULUM_PATH)
    current_curriculum = extract_and_save_all_courses()
    saved_curriculum = load_curriculum(CURRICULUM_PATH)
    if not saved_curriculum.equals(current_curriculum):
        raise ValueError("The extracted curriculum was not saved correctly to curriculum.tsv.")
    logging.info("All courses extracted and saved to curriculum.tsv.")
    added_courses, removed_courses = modified_courses(previous_curriculum, current_curriculum)
    log_changes(added_courses, removed_courses, LOGS_PATH)
    logging.info("Changes (if any) logged to logs.tsv.")


if __name__ == "__main__":
    main()
