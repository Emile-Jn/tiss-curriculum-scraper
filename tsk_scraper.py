# -*- coding: utf-8 -*-
#!/usr/bin/python3

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.safari.service import Service as SafariService
from selenium.webdriver.support.ui import Select
import time
import pandas as pd
from tqdm import tqdm

# Custom module
from table_formatting import *

# Variables
tsk = pd.DataFrame(columns=['module', 'title', 'code', 'type', 'semester', 'credits', 'full_module_name'])
driver = webdriver.Chrome()
tsk_page = "https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?dswid=2955&dsrid=810&date=20241001&key=57214"
driver.get(tsk_page)
time.sleep(3)  # wait 3 seconds to let the page load
# Language of the page is German by default, switch it to English
driver.find_element("id", "language_en").click()
# Wait for the page to reload
time.sleep(3)  # Adjust the sleep time if necessary

# Locate the semester select element
semester_select = Select(driver.find_element('name', 'j_id_2i:semesterSelect'))

empty_list = 0
is_a_list = 0
single_element = 0

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

    n_courses = 0

    for j in tqdm(range(1, len(rows))):  # skip row 0 which just says "Master Data Science"
        # for each row, get the 4 grid cells
        cells = rows[j].find_elements(By.TAG_NAME, "td")
        # if the row is a new section of the curriculum, move to that section
        text = cells[0].text.strip()
        # print(f'matching {text} with {section_names_list[section_number+1]}')
        # Check if the row contains a hyperlink
        hyperlinks = rows[j].find_elements(By.TAG_NAME, "a")
        if len(hyperlinks) == 0:  # if there are no hyperlinks in the row, skip it
            empty_list += 1
            continue
        if isinstance(hyperlinks, list):  # if there are multiple hyperlinks in the row
            is_a_list += 1
            h = hyperlinks[0].get_attribute('href')
        else:
            single_element += 1
            h = ''
        # if h:
        #     print(h)
        if 'tiss.tuwien.ac.at' in str(h):  #if there is at least one tiss hyperlink in the row
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
                {'module': ['TSK'],
                 'title': [course_title],
                 'code': [course_info[0]],
                 'type': [course_info[1]],
                 'semester': [remove_year_info(course_info[2])],
                 'credits': [ects],
                 'full_module_name': ['Transferable Skills']})
            tsk = pd.concat([tsk, new_row], ignore_index=True)
            n_courses += 1
    print('Finished.')

#%% write the tsk courses to a tsv file
tsk.dropna(how='all', inplace=True)
tsk.drop_duplicates(inplace=True)
tsk.to_csv('tsk.tsv', sep='\t', index=False)

driver.quit()  # close the browser
