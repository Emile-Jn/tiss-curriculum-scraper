import pandas as pd


def remove_year_info(semester: str) -> str:
    """Normalize semester strings to W, S, or W and S."""
    normalized = str(semester).lower()
    if "w" in normalized and "s" in normalized:
        return "W and S"
    if "w" in normalized:
        return "W"
    if "s" in normalized:
        return "S"
    return ""


def merge_years(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Remove the year information from the semester column."""
    result = dataframe.copy()
    result["semester"] = result["semester"].apply(remove_year_info)
    return result


def remove_canceled_courses(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Remove courses with 'canceled' in the title."""
    return dataframe[
        ~dataframe["title"].str.contains("canceled", case=False, na=False)
    ].copy()


def modified_courses(
    old_df: pd.DataFrame, new_df: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Find added and removed courses between two curriculum snapshots.
    """
    if "active" not in old_df.columns or "active" not in new_df.columns:
        raise ValueError("Both old_df and new_df must contain an 'active' column")

    id_cols_drop = ["link", "active"]

    def build_id_series(dataframe: pd.DataFrame) -> pd.Series:
        base = dataframe.drop(columns=id_cols_drop, errors="ignore")
        return base.apply(lambda row: tuple(row.tolist()), axis=1)

    old_df_copy = old_df.copy()
    new_df_copy = new_df.copy()
    old_df_copy["__id"] = build_id_series(old_df_copy)
    new_df_copy["__id"] = build_id_series(new_df_copy)

    orphan_old_inactive = old_df_copy[
        (old_df_copy["active"] == False)
        & (~old_df_copy["__id"].isin(new_df_copy["__id"]))
    ]
    if not orphan_old_inactive.empty:
        samples = (
            orphan_old_inactive.drop(columns=["__id"])
            .head(10)
            .to_dict(orient="records")
        )
        raise ValueError(
            "Found inactive courses in old_df that are missing from new_df. "
            f"Examples: {samples}"
        )

    orphan_new_inactive = new_df_copy[
        (new_df_copy["active"] == False)
        & (~new_df_copy["__id"].isin(old_df_copy["__id"]))
    ]
    if not orphan_new_inactive.empty:
        samples = (
            orphan_new_inactive.drop(columns=["__id"])
            .head(10)
            .to_dict(orient="records")
        )
        raise ValueError(
            "Found inactive courses in new_df that were not present in old_df. "
            f"Examples: {samples}"
        )

    added_courses = new_df_copy[
        (new_df_copy["active"] == True)
        & (~new_df_copy["__id"].isin(old_df_copy["__id"]))
    ].drop(columns=["__id"])

    ids_now_inactive = set(
        new_df_copy[new_df_copy["active"] == False]["__id"].tolist()
    )
    removed_courses = old_df_copy[
        (old_df_copy["active"] == True) & (old_df_copy["__id"].isin(ids_now_inactive))
    ].drop(columns=["__id"])

    return added_courses, removed_courses
