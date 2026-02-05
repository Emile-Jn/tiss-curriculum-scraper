# -*- coding: utf-8 -*-
#!/usr/bin/python3

# Third-party modules
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import chromedriver_autoinstaller
import time
from datetime import date
from tqdm import tqdm

# Custom module
from table_formatting import *

# Constants
SECTION_NAMES = {
    "Prüfungsfach Data Science - Foundations": "Foundations",
    "Prüfungsfach Domain-Specific Aspects of Data Science": "DSA",
    "Modul FDS/CO - Fundamentals of Data Science - Core": "FDS/CO",
    "Modul FDS/EX - Fundamentals of Data Science - Extension": "FDS/EX",
    "Modul MLS/CO - Machine Learning and Statistics - Core": "MLS/CO",
    "Modul MLS/EX - Machine Learning and Statistics - Extension": "MLS/EX",
    "Modul BDHPC/CO - Big Data and High Performance Computing - Core": "BDHPC/CO",
    "Modul BDHPC/EX - Big Data and High Performance Computing - Extension": "BDHPC/EX",
    "Modul VAST/CO - Visual Analytics and Semantic Technologies - Core": "VAST/CO",
    "Modul VAST/EX - Visual Analytics and Semantic Technologies - Extension": "VAST/EX",
    "Prüfungsfach Freie Wahlfächer und Transferable Skills": "Free Electives",
}
THESIS_MODULE = pd.DataFrame(
    {'module': ['Thesis', 'Thesis', 'Thesis'],
     'title': ['Master Thesis', 'Seminar for Master students in Data Science', 'Defense of Master Thesis'],
     'code': ['none', '180.772', 'none'],  # arbitrary code 'none' for the thesis
     'type': ['', 'SE', ''],
     'semester': ['W and S', 'W and S', 'W and S'],  # Winter and Summer
     'credits': [27, 1.5, 1.5]})
# TODO: instead of adding it manually, scrape the thesis seminar in case its info changes in the future?

#%% functions

def initiate_chrome_driver() -> webdriver.Chrome:
    """
    Initiate a headless Chrome WebDriver to scrape Tiss from any device (including GitHub Actions).
    Returns:
        webdriver.Chrome: the initiated Chrome WebDriver
    """
    chromedriver_autoinstaller.install()  # Check if the current version of chromedriver exists
    # and if it doesn't exist, download it automatically,
    # then add chromedriver to path

    chrome_options = webdriver.ChromeOptions()
    options = [
        "--window-size=1200,1200",
        "--ignore-certificate-errors",
        "--headless",
        "--disable-gpu",
        "--disable-extensions",
        "--no-sandbox",
        "--disable-dev-shm-usage",
    ]
    for option in options:
        chrome_options.add_argument(option)

    driver = webdriver.Chrome(options=chrome_options)
    return driver


def scrape_curriculum_page(url: str, driver: webdriver.Chrome, section_names: dict=None) -> pd.DataFrame:
    """
    Open the curriculum page at URL using the provided WebDriver, scrape the curriculum
    table for all available semesters line by line, and return a dataframe with all courses.
    Args:
        url: the full URL of the curriculum page to scrape
        driver: the Selenium WebDriver to use for scraping
        section_names: the names of the different modules in the Data Science curriculum

    Returns:
        all courses on the page as a pandas dataframe
    """
    columns = ['title', 'code', 'type', 'semester', 'credits', 'link']
    if section_names is not None:  # if using section names to extract modules
        columns.insert(0, 'module')
        columns.append('full_module_name')
    curriculum = pd.DataFrame(columns=columns)

    try:
        driver.get(url)
    except Exception as e:
        print("Driver failed, restarting WebDriver:", e)
        driver.quit()
        driver = initiate_chrome_driver()  # Restart the WebDriver
        driver.get(url)
    time.sleep(3)  # wait 3 seconds to let the page load
    # driver.implicitly_wait(0.5)  # not needed?
    # Language of the page is German by default, switch it to English
    try:  # try to switch to English if the page is in German
        driver.find_element("id", "language_en").click()
    except NoSuchElementException:
        pass  # leave the page in English if it's already in English
    # Wait for the page to reload
    time.sleep(3)  # Adjust the sleep time if necessary
    # Locate the semester select element
    semester_select = Select(driver.find_element('name', 'j_id_2i:semesterSelect'))
    # For each semester, select it and scrape the courses:
    for i in range(len(semester_select.options)):
        # Re-locate the semester select element
        semester_select = Select(driver.find_element('name', 'j_id_2i:semesterSelect'))
        # Get the updated option reference
        semester = semester_select.options[i]
        # Select each semester by visible text
        semester_select.select_by_visible_text(semester.text)
        print(f'\n Processing the semester {semester.text} \n Waiting 3 seconds to load the page...')
        time.sleep(3)  # wait 3 seconds to let the page load
        table = driver.find_element(By.ID, "j_id_2i:nodeTable_data")
        rows = table.find_elements(By.TAG_NAME, "tr")
        curriculum = scrape_rows(rows, curriculum, section_names)
        print('Finished scraping all courses available in the semester.')
    return curriculum


def scrape_rows(rows, curriculum: pd.DataFrame, section_names: dict=None) -> pd.DataFrame:
    """
    Add the valid courses found in rows to the curriculum dataframe.
    Args
        rows: a html element containing the rows of the curriculum table
        curriculum: a pandas dataframe in which each row is a course
        section_names: the names of the sections in the curriculum, which are modules
    Returns:
        the curriculum dataframe with the new courses added
    """
    n_courses = 0
    if section_names is not None:
        section_names_list = list(section_names.keys())
        section_number = -1 # start with no section

    # For each row in the table, scrape the course information
    for j in tqdm(range(1, len(rows))):  # skip row 0 which just says "Master Data Science"
        if section_names is not None:  # if using section names to extract modules
            if section_number == -1 and  j > 3:
                raise ValueError("Could not find the first section of the curriculum in the first 3 rows.")
        # for each row, get the 4 grid cells
        cells = rows[j].find_elements(By.TAG_NAME, "td")
        # if the row is a new section of the curriculum, move to that section
        text = cells[0].text.strip()
        # print(f'matching {text} with {section_names_list[section_number+1]}')
        if section_names is not None:  # if using section names to extract modules
            if text == section_names_list[section_number + 1]:
                section_number += 1
                if section_number > len(SECTION_NAMES) - 2:
                    break
                continue
        # Check if the row contains a hyperlink
        hyperlinks = rows[j].find_elements(By.TAG_NAME, "a")
        if hyperlinks:  #if there is at least one hyperlink in the row
            first_link = hyperlinks[0].get_attribute('href')
            if 'tiss.tuwien.ac.at/course/courseDetails.xhtml' in first_link:  #if there is at least one tiss hyperlink in the row
                new_row = get_course(cells)
                new_row['link'] = first_link  # add the URL of the course
                if section_names is not None:  # if using section names to extract modules
                    new_row['module'] = section_names[section_names_list[section_number]]
                    new_row['full_module_name'] = section_names_list[section_number]
                curriculum = pd.concat([curriculum, new_row], ignore_index=True)
                n_courses += 1
    print(f'Found {n_courses} courses in the current semester.')
    return curriculum


def get_course(cells) -> pd.DataFrame:
    """
    Extract the course information from the given row cells.
    Args:
        cells: HTML elements containing the 4 grid cells of a course row

    Returns:
        a pandas dataframe with a single row containing the course information
    """
    # get the title of the course
    course_title = cells[0].find_element(By.CLASS_NAME, "courseTitle").text.strip()
    # get the course key
    course_key = cells[0].find_element(By.CLASS_NAME, "courseKey").text.strip()
    # split the course key into the course code, type, and semester
    course_info = course_key.split(" ")
    # get the number of ECTS credits from the last cell in the row
    ects = float(cells[3].text)
    # make a new course object
    new_row = pd.DataFrame(
        {'title': [course_title],
         'code': [str(course_info[0])],
         'type': [course_info[1]],
         'semester': [course_info[2]],
         'credits': [ects]})
    return new_row

def get_data_science_curriculum(driver):
    """
    Use the driver to obtain the complete data science curriculum with thesis module
    Args:
        driver: the Selenium WebDriver to use for scraping

    Returns:
        The full curriculum as a pandas dataframe
    """
    URL = "https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?dswid=7871&dsrid=370&key=67853"
    curriculum = scrape_curriculum_page(URL, driver, SECTION_NAMES)
    return pd.concat([curriculum, THESIS_MODULE], ignore_index=True)

def get_tsk_courses(driver):
    """
    Use the driver to obtain the TSK courses
    Args:
        driver: the Selenium WebDriver to use for scraping

    Returns:
        All TSK courses as a pandas dataframe
    """
    URL = "https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?dswid=2955&dsrid=810&date=20241001&key=57214"
    tsk_courses = scrape_curriculum_page(URL, driver)
    tsk_courses['module'] = 'TSK'
    tsk_courses['full_module_name'] = 'Modul Freie Wahlfächer und Transferable Skills'
    return tsk_courses

def clean_curriculum(curriculum: pd.DataFrame) -> pd.DataFrame:
    """
    Remove duplicates and canceled courses from the curriculum and remove rows with all missing values.
    Args:
        curriculum: all courses in a pandas dataframe

    Returns:
        the cleaned curriculum as a pandas dataframe
    """
    curriculum = merge_years(curriculum)
    curriculum = remove_canceled_courses(curriculum)
    """ Remove duplicates, taking everything into account except the link AND the code.
    Reasoning: if a course has a new code but all else is the same, there is no reason
    to show it twice in the curriculum. If the number of credits has changed however, it
    is useful for users to be able to select both versions of the course.
    """
    before_drop_duplicates = curriculum.shape[0]
    curriculum.drop_duplicates(subset=curriculum.columns.difference(['link', 'code']),
                               inplace=True,
                               keep='last')  # keep the most recent available course
    after_drop_duplicates = curriculum.shape[0]
    print(f'Removed {before_drop_duplicates - after_drop_duplicates} duplicates.')
    curriculum.dropna(how='all', inplace=True)
    after_drop_na = curriculum.shape[0]
    print(f'Removed {after_drop_duplicates - after_drop_na} rows with all missing values.')
    return curriculum

def extract_and_save_all_courses() -> pd.DataFrame:
    """
    Extract all courses from the curriculum and TSK pages, clean the data,
    compare with the previous curriculum, save the new curriculum to curriculum.tsv,
    and return the new curriculum dataframe.
    Returns:
        all courses in the final format as a pandas dataframe
    """
    # TODO: merge scraped courses with previous curriculum, add "active" column to indicate if the course is still in Tiss
    previous_curriculum = pd.read_csv('curriculum.tsv', sep='\t')
    driver = initiate_chrome_driver()
    curriculum = get_data_science_curriculum(driver)
    tsk_courses = get_tsk_courses(driver)
    driver.quit()
    all_courses = pd.concat([curriculum, tsk_courses], ignore_index=True)
    all_courses = clean_curriculum(all_courses)
    new_changes = all_courses[~all_courses['code'].isin(previous_curriculum['code'])]
    all_courses.to_csv('curriculum.tsv', sep='\t', index=False)
    return all_courses

def log_changes(added_courses, removed_courses):
    """Append detected changes to logs.tsv with a timestamp."""
    with open("logs.tsv", "a", encoding="utf-8") as log_file:
        timestamp = date.today().strftime("%Y-%m-%d")
        if not added_courses.empty:
            for _, row in added_courses.iterrows():
                log_file.write(f"{timestamp}\tadded\t{row['module']}\t{row['title']}\t{row['code']}\t{row['type']}\t{row['semester']}\t{row['credits']}\n")
        if not removed_courses.empty:
            for _, row in removed_courses.iterrows():
                log_file.write(f"{timestamp}\tremoved\t{row['module']}\t{row['title']}\t{row['code']}\t{row['type']}\t{row['semester']}\t{row['credits']}\n")
    print("Changes (if any) logged to logs.tsv.")

def main():
    # TODO: make safety checks, return error message if scraping fails
    old_curriculum = pd.read_csv('curriculum.tsv', sep='\t')
    all_courses = extract_and_save_all_courses()
    print('All courses extracted and saved to curriculum.tsv.')

    new_curriculum = pd.read_csv('curriculum.tsv', sep='\t')
    added_courses, removed_courses = modified_courses(new_curriculum, old_curriculum)
    log_changes(added_courses, removed_courses)  # save a record of the added and removed courses

if __name__ == '__main__':
    main()
