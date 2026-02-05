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

def modified_courses(new_df: pd.DataFrame, old_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Find the added courses that are in new_df but not in old_df
    and the removed courses that are in old_df but not in new_df
    """
    # Remove the link column from both dataframes
    new_df_copy = new_df.drop(columns='link', errors='ignore')
    old_df_copy = old_df.drop(columns='link', errors='ignore')
    # Find the rows in new_df that are not in old_df
    new_df_copy['key'] = new_df_copy.apply(tuple, axis=1)
    old_df_copy['key'] = old_df_copy.apply(tuple, axis=1)
    added_courses = new_df_copy[~new_df_copy['key'].isin(old_df_copy['key'])].drop(columns=['key'])
    removed_courses = old_df_copy[~old_df_copy['key'].isin(new_df_copy['key'])].drop(columns=['key'])
    return added_courses, removed_courses
