"""
date: 8/11/2024
author: Emile Johnston

Some functions to clean up the raw output of the scraping functions in scraper.py.
"""
import pandas as pd

def remove_year_info(sem: str) -> str:
    """
    Remove the year information from the sem column
    :param sem: e.g. '2024W' or 'S'
    :return:
    """
    if 'w' in sem.lower() and 's' in sem.lower():
        return 'W and S'
    if 'w' in sem.lower():
        return 'W'
    if 's' in sem.lower():
        return 'S'
    print('Warning: course has no semester information (winter or summer).')
    return ''

def merge_years(df: pd.DataFrame) -> pd.DataFrame:
    """Remove the year information from the semester column"""
    df['semester'] = df['semester'].apply(remove_year_info)
    return df

def remove_canceled_courses(df: pd.DataFrame) -> pd.DataFrame:
    """Remove courses with 'canceled' in the title"""
    rows_before = df.shape[0]
    df = df[~df['title'].str.contains('canceled', case=False)]
    print(f'Removed {rows_before - df.shape[0]} canceled courses.')
    return df

def modified_courses(old_df: pd.DataFrame, new_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Find the added courses that are in new_df but not in old_df
    and the removed courses that are in old_df but not in new_df.

    Behavior changes:
    - added_courses: rows in new_df with active == True and whose identity
      (all columns except 'link' and 'active') is not present in old_df.
    - removed_courses: rows in old_df with active == True whose identity is
      present in new_df but there with active == False.
    - If a course is in old_df with active == False and isn't in new_df -> raise ValueError.
    - If a course is in new_df with active == False and isn't in old_df -> raise ValueError.
    """
    # Ensure active column exists in both frames
    if 'active' not in old_df.columns or 'active' not in new_df.columns:
        raise ValueError("Both old_df and new_df must contain an 'active' column")

    # Build an identity key that represents a course irrespective of its `active` state or `link`.
    id_cols_drop = ['link', 'active']

    def build_id_series(df: pd.DataFrame) -> pd.Series:
        base = df.drop(columns=id_cols_drop, errors='ignore')
        # Convert each row to a tuple to use as a stable identity key
        return base.apply(lambda r: tuple(r.tolist()), axis=1)

    old_df_copy = old_df.copy()
    new_df_copy = new_df.copy()

    old_df_copy['__id'] = build_id_series(old_df_copy)
    new_df_copy['__id'] = build_id_series(new_df_copy)

    # Error: any course that was inactive in old_df but is completely missing from new_df
    orphan_old_inactive = old_df_copy[(old_df_copy['active'] == False) & (~old_df_copy['__id'].isin(new_df_copy['__id']))]
    if not orphan_old_inactive.empty:
        # Provide some context for the error: first few offending rows
        samples = orphan_old_inactive.drop(columns=['__id']).head(10).to_dict(orient='records')
        raise ValueError(f"Found {len(orphan_old_inactive)} courses that were inactive in old_df but are missing from new_df. Examples: {samples}")

    # Error: any course that is inactive in new_df but wasn't present in old_df
    orphan_new_inactive = new_df_copy[(new_df_copy['active'] == False) & (~new_df_copy['__id'].isin(old_df_copy['__id']))]
    if not orphan_new_inactive.empty:
        samples = orphan_new_inactive.drop(columns=['__id']).head(10).to_dict(orient='records')
        raise ValueError(f"Found {len(orphan_new_inactive)} courses that are inactive in new_df but were not present in old_df. Examples: {samples}")

    # Added courses: present in new_df, active == True, and identity not in old_df
    added_courses = new_df_copy[(new_df_copy['active'] == True) & (~new_df_copy['__id'].isin(old_df_copy['__id']))].drop(columns=['__id'])

    # Removed courses: were active in old_df and in new_df the same identity exists but is inactive
    ids_now_inactive = set(new_df_copy[new_df_copy['active'] == False]['__id'].tolist())
    removed_courses = old_df_copy[(old_df_copy['active'] == True) & (old_df_copy['__id'].isin(ids_now_inactive))].drop(columns=['__id'])

    return added_courses, removed_courses
