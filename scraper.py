# -*- coding: utf-8 -*-
#!/usr/bin/python3

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.safari.service import Service as SafariService
from selenium.webdriver.support.ui import Select
import chromedriver_autoinstaller
import time
import pandas as pd
from tqdm import tqdm

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
SECTION_NAMES_LIST = list(SECTION_NAMES.keys())

# Variables
curriculum = pd.DataFrame(
    columns=[
        "module",
        "title",
        "code",
        "type",
        "semester",
        "credits",
        "full_module_name",
    ]
)

# TODO: adapt code for other browsers
# service = SafariService('/usr/bin/safaridriver')
# driver = webdriver.Safari(service=service)
chromedriver_autoinstaller.install()  # Check if the current version of chromedriver exists
# and if it doesn't exist, download it automatically,
# then add chromedriver to path

chrome_options = webdriver.ChromeOptions()
# Add your options as needed
options = [
    "--window-size=1200,1200",
    "--ignore-certificate-errors",
]

driver = webdriver.Chrome(options=chrome_options)

driver.get(
    "https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?dswid=7871&dsrid=370&key=67853"
)
time.sleep(3)  # wait 3 seconds to let the page load
driver.implicitly_wait(0.5)
# Language of the page is German by default, switch it to English
driver.find_element("id", "language_en").click()
# Wait for the page to reload
time.sleep(3)  # Adjust the sleep time if necessary

# Locate the semester select element
semester_select = Select(driver.find_element("name", "j_id_2i:semesterSelect"))

for i in range(len(semester_select.options)):
    # Re-locate the semester select element
    semester_select = Select(driver.find_element("name", "j_id_2i:semesterSelect"))
    # Get the updated option reference
    semester = semester_select.options[i]
    # Select each semester by visible text
    semester_select.select_by_visible_text(
        semester.text
    )  # TODO: error for switching semester
    print(
        f"\n Processing the semester {semester.text} \n Waiting 3 seconds to load the page..."
    )
    time.sleep(3)  # wait 3 seconds to let the page load
    table = driver.find_element(By.ID, "j_id_2i:nodeTable_data")
    rows = table.find_elements(By.TAG_NAME, "tr")

    n_courses = 0
    section_number = -1  # start with no section

    for j in tqdm(
        range(1, len(rows))
    ):  # skip row 0 which just says "Master Data Science"
        # n_courses = parse_row(rows, j)
        if section_number == -1 and j > 3:
            raise ValueError(
                "Could not find the first section of the curriculum in the first 3 rows."
            )
        # for each rows, get the 4 grid cells
        cells = rows[j].find_elements(By.TAG_NAME, "td")
        # if the row is a new section of the curriculum, move to that section
        text = cells[0].text.strip()
        # print(f'matching {text} with {section_names_list[section_number+1]}')
        if text == SECTION_NAMES_LIST[section_number + 1]:
            section_number += 1
            if section_number > len(SECTION_NAMES) - 2:
                break
            continue
        # Check if the row contains a hyperlink
        hyperlinks = rows[j].find_elements(By.TAG_NAME, "a")
        if hyperlinks:  # if there is at least one hyperlink in the row
            # get the course key
            course_key = cells[0].find_element(By.CLASS_NAME, "courseKey").text.strip()
            # get the title of the course
            course_title = (
                cells[0].find_element(By.CLASS_NAME, "courseTitle").text.strip()
            )
            # split the course key into the course code, type, and semester
            course_info = course_key.split(" ")
            # get the number of ECTS credits from the last cell in the row
            ects = float(cells[3].text)
            # make a new course object
            new_row = pd.DataFrame(
                {
                    "module": [SECTION_NAMES[SECTION_NAMES_LIST[section_number]]],
                    "title": [course_title],
                    "code": [course_info[0]],
                    "type": [course_info[1]],
                    "semester": [course_info[2]],
                    "credits": [ects],
                    "full_module_name": [SECTION_NAMES_LIST[section_number]],
                }
            )
            # print(f'type(curriculum): {type(curriculum)}')
            # print(f'type(new_row): {type(new_row)}')
            curriculum = pd.concat([curriculum, new_row], ignore_index=True)
            n_courses += 1
            # print(f'\r Processed {n_courses} courses.', end='')

    print("Finished.")


def parse_row(rows, j, n_courses, section_number):
    if section_number == -1 and j > 3:
        raise ValueError(
            "Could not find the first section of the curriculum in the first 3 rows."
        )
        # for each rows, get the 4 grid cells
    cells = rows[j].find_elements(By.TAG_NAME, "td")
    # if the row is a new section of the curriculum, move to that section
    text = cells[0].text.strip()
    # print(f'matching {text} with {section_names_list[section_number+1]}')
    if text == SECTION_NAMES_LIST[section_number + 1]:
        section_number += 1
        if section_number > len(SECTION_NAMES) - 2:
            return "stop"
        # continue
    # Check if the row contains a hyperlink
    hyperlinks = rows[j].find_elements(By.TAG_NAME, "a")
    if hyperlinks:  # if there is at least one hyperlink in the row
        add_course(cells)
        return n_courses + 1
    # otherwise, no new course is added
    return n_courses


def add_course(cells):
    global curriculum
    # get the course key
    course_key = cells[0].find_element(By.CLASS_NAME, "courseKey").text.strip()
    # get the title of the course
    course_title = cells[0].find_element(By.CLASS_NAME, "courseTitle").text.strip()
    # split the course key into the course code, type, and semester
    course_info = course_key.split(" ")
    # get the number of ECTS credits from the last cell in the row
    ects = float(cells[3].text)
    # make a new course object
    new_row = pd.DataFrame(
        {
            "module": [SECTION_NAMES[SECTION_NAMES_LIST[section_number]]],
            "title": [course_title],
            "code": [course_info[0]],
            "type": [course_info[1]],
            "semester": [course_info[2]],
            "credits": [ects],
        }
    )
    curriculum = pd.concat([curriculum, new_row], ignore_index=True)
    # print(f'\r Processed {n_courses+1} courses.', end='')


# %% Manually add the thesis, seminar and defense, which don't appear as normal tiss courses
thesis_module = pd.DataFrame(
    {
        "module": ["Thesis", "Thesis", "Thesis"],
        "title": [
            "Master Thesis",
            "Seminar for Master students in Data Science",
            "Defense of Master Thesis",
        ],
        "code": ["1", "180.722", "2"],  # arbitrary codes 1 and 2 for thesis and defense
        "type": ["", "SE", ""],
        "semester": ["W and S", "W and S", "W and S"],  # Winter and Summer
        "credits": [27, 1.5, 1.5],
    }
)

curriculum = pd.concat([curriculum, thesis_module], ignore_index=True)
curriculum = curriculum.dropna(how="all")  # drop rows with all NaN values
curriculum.drop_duplicates(inplace=True)

# %% write the curriculum to a tsv file
curriculum.to_csv("curriculum.tsv", sep="\t", index=False)

driver.quit()  # close the browser
