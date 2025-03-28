"""
date: 8/11/2024
author: Emile Johnston

Some functions to clean up the raw output of the scraping functions in scraper.py.
"""
import pandas as pd
from datetime import datetime

def same_season(season_1: str, season_2: str) -> bool:
    """
    Check if two strings refer to the same academic season
    :param season_1: e.g. 'W' or 's' or '2024W'
    :param season_2: same as season_1
    :return: True if the two strings refer to the same season
    """
    if 'w' in season_1.lower() and 'w' in season_2.lower():
        return True
    if 's' in season_1.lower() and 's' in season_2.lower():
        return True
    return False

def later_year(year_1: str, year_2: str) -> bool:
    """Check if year_1 is later than year_2"""
    if int(year_1) > int(year_2):
        return True
    return False

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

def make_url(course_code, semester, year=None) -> str:
    if not '.' in course_code:  # codes without a dot are artificially created
        return ''
    code = course_code.replace('.', '')  # remove the dot in the course code
    if len(code) != 6:  # course codes must be six digits
        return ''
    if not isinstance(year, int):
        raise ValueError('Year must be an integer.')
    if year < 2023:
        raise ValueError('Year must be at least 2023.')
    if year is None:
        year = get_current_course_year(semester)
    return f'https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr={code}&semester={year}{semester}'

def get_current_course_year(semester: str) -> int:
    """Get the current year of the course"""
    now = datetime.now()
    if 'w' in semester.lower():
        if now.month < 10:  # if this year's winter semester has not started yet
            return now.year - 1  # use last year's information
        return now.year  # use the current information
    if 's' in semester.lower():
        if now.month < 3:  # if this year's summer semester has not started yet
            return now.year - 1  # use last year's information
        return now.year  # use the current information
