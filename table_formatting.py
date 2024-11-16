"""
date: 8/11/2024
author: Emile Johnston
"""
import pandas as pd

def same_season(season_1: str, season_2: str) -> bool:
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

def remove_year_duplicates():
    curr = pd.read_csv('curriculum.tsv', sep='\t')

    """
    new_curr = pd.DataFrame(columns=curr.columns)  # Empty dataframe with the same columns
    for i in range(len(curr)):
        row = curr.iloc[i]  #  a course in the original curriculum
        matches = new_curr[(new_curr['code'] == row['code'])]  # the same course
        if len(matches) == 0:  # the course is not yet added
            new_curr = pd.concat([new_curr, row.to_frame().T], ignore_index=True)
        else:
            for course in matches.iterrows():
                if same_season(row['semester'], course['semester']):
                    if later_year(row['semester'][-4:], match['semester'][-4:]):
                    new_curr = new_curr.drop(new_curr[new_curr['code'] == row['code']].index)
                    new_curr = pd.concat([new_curr, row.to_frame().T], ignore_index=True)
                else:
                    new_curr = pd.concat([new_curr, row.to_frame().T], ignore_index=True)

        """

def remove_year_info(sem: str) -> str:
    """Remove the year information from the sem column"""
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
    df = df[~df['title'].str.contains('canceled', case=False)]
    return df

def compare_df(new_df: pd.DataFrame, old_df: pd.DataFrame) -> pd.DataFrame:
    """Compare two dataframes and return the differences"""
    if not ('link' in new_df.columns and 'link' in old_df.columns):
        # Remove the link column from both dataframes
        new_df = new_df.drop(columns='link', errors='ignore')
        old_df = old_df.drop(columns='link', errors='ignore')
    # Find the rows in df1 that are not in df2
    new_rows = new_df.merge(old_df, on=list(new_df.columns), indicator=True, how='left')
    return new_rows[new_rows['_merge'] == 'left_only']


if __name__ == '__main__':  # clean up the existing tsv file
    curriculum = pd.read_csv('curriculum.tsv', sep='\t')
    #%%
    thesis_module = pd.DataFrame(
        {'module': ['Thesis'] * 3,
         'title': ['Master Thesis', 'Seminar for Master students in Data Science', 'Defense of Master Thesis'],
         'code': ['1', '180.722', '2'],  # arbitrary codes 1 and 2 for thesis and defense
         'type': ['N/A', 'SE', 'N/A'],
         'semester': ['W and S'] * 3,  # Winter and Summer
         'credits': [27, 1.5, 1.5],
         'full_module_name': ['Diplomarbeit und kommissionelle Gesamtprüfung'] * 3})
    curriculum = pd.concat([curriculum, thesis_module], ignore_index=True)
    curriculum = merge_years(curriculum)
    curriculum.drop_duplicates(inplace=True)
    curriculum.dropna(how='all', inplace=True)
    #%%
    curriculum = remove_canceled_courses(curriculum)
    curriculum.to_csv('curriculum.tsv', sep='\t', index=False)
