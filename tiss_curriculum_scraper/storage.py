from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd


def load_curriculum(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep="\t")


def save_curriculum(dataframe: pd.DataFrame, path: Path) -> None:
    dataframe.to_csv(path, sep="\t", index=False)


def log_changes(added_courses: pd.DataFrame, removed_courses: pd.DataFrame, path: Path) -> None:
    timestamp = date.today().strftime("%Y-%m-%d")
    with path.open("a", encoding="utf-8") as log_file:
        for _, row in added_courses.iterrows():
            log_file.write(
                f"{timestamp}\tadded\t{row['module']}\t{row['title']}\t{row['code']}"
                f"\t{row['type']}\t{row['semester']}\t{row['credits']}\n"
            )
        for _, row in removed_courses.iterrows():
            log_file.write(
                f"{timestamp}\tremoved\t{row['module']}\t{row['title']}\t{row['code']}"
                f"\t{row['type']}\t{row['semester']}\t{row['credits']}\n"
            )
