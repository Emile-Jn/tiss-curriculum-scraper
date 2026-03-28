from __future__ import annotations

import logging
import re
import unicodedata

import pandas as pd
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from .browser import initiate_chrome_driver
from .constants import DATA_SCIENCE_URL, SECTION_NAMES, THESIS_MODULE, TSK_URL
from .formatting import merge_years, remove_canceled_courses

LOGGER = logging.getLogger(__name__)

BASE_COLUMNS = ["title", "code", "type", "semester", "credits", "link"]
MODULE_COLUMNS = ["module", *BASE_COLUMNS, "full_module_name"]


def normalize_text(value: str) -> str:
    """Normalize text so selectors are resilient to accent variations."""
    return unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")


def create_empty_curriculum(use_modules: bool) -> pd.DataFrame:
    columns = MODULE_COLUMNS if use_modules else BASE_COLUMNS
    dataframe = pd.DataFrame(columns=columns)
    dtypes = {column: "str" for column in columns}
    dtypes["credits"] = "float64"
    return dataframe.astype(dtypes)


def wait_for_page_ready(driver) -> None:
    wait = WebDriverWait(driver, 15)
    wait.until(
        lambda current_driver: current_driver.execute_script("return document.readyState")
        == "complete"
    )
    wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "select[name$='semesterSelect']"))
    )
    wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "tbody[id$='nodeTable_data']"))
    )


def wait_for_document_ready(driver) -> None:
    wait = WebDriverWait(driver, 15)
    wait.until(
        lambda current_driver: current_driver.execute_script("return document.readyState")
        == "complete"
    )
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))


def ensure_english_language(driver) -> None:
    try:
        language_toggle = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "language_en"))
        )
        language_toggle.click()
        wait_for_page_ready(driver)
    except (NoSuchElementException, TimeoutException):
        LOGGER.debug("Page is already in English or language toggle is unavailable")


def load_page(driver, url: str, expect_curriculum_controls: bool = True):
    wait_function = wait_for_page_ready if expect_curriculum_controls else wait_for_document_ready
    try:
        driver.get(url)
        wait_function(driver)
        ensure_english_language(driver)
        return driver
    except WebDriverException as error:
        LOGGER.warning("Driver failed while loading %s, restarting: %s", url, error)
        try:
            driver.quit()
        except WebDriverException:
            LOGGER.debug("Failed to quit old driver during restart", exc_info=True)
        restarted_driver = initiate_chrome_driver()
        restarted_driver.get(url)
        wait_function(restarted_driver)
        ensure_english_language(restarted_driver)
        return restarted_driver


def semester_select(driver) -> Select:
    element = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "select[name$='semesterSelect']"))
    )
    return Select(element)


def curriculum_rows(driver) -> list[WebElement]:
    table = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "tbody[id$='nodeTable_data']"))
    )
    return table.find_elements(By.TAG_NAME, "tr")


def switch_semester(driver, option_text: str) -> None:
    """Switch the selected semester and wait for the table to settle."""
    current_select = semester_select(driver)
    if current_select.first_selected_option.text == option_text:
        wait_for_page_ready(driver)
        return

    previous_table = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "tbody[id$='nodeTable_data']"))
    )
    current_select.select_by_visible_text(option_text)

    try:
        WebDriverWait(driver, 15).until(EC.staleness_of(previous_table))
    except TimeoutException:
        LOGGER.debug("Semester %s did not replace the table element before timeout", option_text)

    wait_for_page_ready(driver)
    WebDriverWait(driver, 15).until(
        lambda current_driver: semester_select(current_driver).first_selected_option.text
        == option_text
    )


def parse_course_info(course_key: str) -> tuple[str, str, str]:
    parts = course_key.split()
    if len(parts) < 3:
        raise ValueError(f"Unexpected course key format: {course_key!r}")
    return str(parts[0]), parts[1], parts[2]


def extract_ects_from_html(html: str, url: str) -> float:
    """Parse the numeric credits value from a TISS course HTML page."""
    properties_match = re.search(
        r"<h2>\s*Properties\s*</h2>\s*<ul[^>]*>(.*?)</ul>",
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if properties_match is None:
        raise ValueError(f"Could not find the Properties section at {url}.")

    credits_match = re.search(
        r"<li>\s*Credits:\s*([0-9]+(?:\.[0-9]+)?)\s*</li>",
        properties_match.group(1),
        flags=re.IGNORECASE | re.DOTALL,
    )
    if credits_match is None:
        raise ValueError(f"Could not find a Credits value in the Properties section at {url}.")

    return float(credits_match.group(1))


def extract_ects(url: str) -> float:
    """Fetch a TISS course page and return its numeric credits value."""
    driver = initiate_chrome_driver()
    try:
        driver = load_page(driver, url, expect_curriculum_controls=False)
        page_text = driver.find_element(By.TAG_NAME, "body").text
    finally:
        driver.quit()

    match = re.search(
        r"\b(?:Credits|ECTS)\b\s*[:\n]?\s*([0-9]+(?:\.[0-9]+)?)",
        page_text,
        flags=re.IGNORECASE,
    )
    if match is None:
        raise ValueError(f"Could not find a Credits value on the course page at {url}.")
    return float(match.group(1))


def build_course_row(
    course_title: str, course_key: str, credits_text: str, link: str
) -> dict[str, object]:
    code, course_type, semester = parse_course_info(course_key)
    try:
        credits = float(credits_text)
    except ValueError:
        LOGGER.info("No valid ECTS found inline for %s, falling back to course page", course_title)
        credits = extract_ects(link)
    if credits < 0.5:
        raise ValueError(
            f"ECTS credits for course {course_title} is less than 0.5, which is unlikely to be correct."
        )

    return {
        "title": course_title.replace("\t", " "),
        "code": code,
        "type": course_type,
        "semester": semester,
        "credits": credits,
        "link": link,
    }


def get_course(cells: list[WebElement], link: str) -> pd.DataFrame:
    course_title = cells[0].find_element(By.CLASS_NAME, "courseTitle").text.strip()
    course_key = cells[0].find_element(By.CLASS_NAME, "courseKey").text.strip()
    row = build_course_row(course_title, course_key, cells[3].text, link)
    return pd.DataFrame([row])


def scrape_rows(
    rows: list[WebElement], curriculum: pd.DataFrame, section_names: dict[str, str] | None = None
) -> pd.DataFrame:
    n_courses = 0
    normalized_sections = (
        {normalize_text(name): (section_names[name], name) for name in section_names}
        if section_names
        else {}
    )
    current_module_name: str | None = None
    current_module_label: str | None = None

    row_index = 1
    while row_index < len(rows):
        for attempt in range(3):
            try:
                row = rows[row_index]
                cells = row.find_elements(By.TAG_NAME, "td")
                break
            except StaleElementReferenceException:
                if attempt == 2:
                    raise
                rows = row.parent.find_elements(By.TAG_NAME, "tr")
        else:
            row_index += 1
            continue

        if not cells:
            row_index += 1
            continue

        text = normalize_text(cells[0].text.strip())
        if section_names is not None and text in normalized_sections:
            current_module_name, current_module_label = normalized_sections[text]
            row_index += 1
            continue

        try:
            hyperlinks = row.find_elements(By.TAG_NAME, "a")
        except StaleElementReferenceException:
            rows = row.parent.find_elements(By.TAG_NAME, "tr")
            continue
        if not hyperlinks:
            row_index += 1
            continue

        first_link = hyperlinks[0].get_attribute("href")
        if not first_link or "tiss.tuwien.ac.at/course/courseDetails.xhtml" not in first_link:
            row_index += 1
            continue

        try:
            new_row = get_course(cells, first_link)
        except StaleElementReferenceException:
            rows = row.parent.find_elements(By.TAG_NAME, "tr")
            continue
        if section_names is not None:
            if current_module_name is None or current_module_label is None:
                raise ValueError("Could not determine the curriculum section before encountering courses.")
            new_row["module"] = current_module_name
            new_row["full_module_name"] = current_module_label
            new_row = new_row[MODULE_COLUMNS]
        curriculum = pd.concat([curriculum, new_row], ignore_index=True)
        n_courses += 1
        row_index += 1

    LOGGER.info("Found %s courses in the current semester", n_courses)
    return curriculum


def scrape_curriculum_page(
    url: str, driver, section_names: dict[str, str] | None = None
) -> tuple[pd.DataFrame, object]:
    curriculum = create_empty_curriculum(use_modules=section_names is not None)
    driver = load_page(driver, url)
    option_texts = [option.text for option in semester_select(driver).options]

    for option_text in option_texts:
        LOGGER.info("Processing semester %s", option_text)
        switch_semester(driver, option_text)
        rows = curriculum_rows(driver)
        curriculum = scrape_rows(rows, curriculum, section_names)

    return curriculum, driver


def get_data_science_curriculum(driver) -> tuple[pd.DataFrame, object]:
    LOGGER.info("Scraping the Data Science curriculum")
    curriculum, driver = scrape_curriculum_page(DATA_SCIENCE_URL, driver, SECTION_NAMES)
    return pd.concat([curriculum, THESIS_MODULE], ignore_index=True), driver


def get_tsk_courses(driver) -> tuple[pd.DataFrame, object]:
    LOGGER.info("Scraping the TSK courses")
    tsk_courses, driver = scrape_curriculum_page(TSK_URL, driver)
    tsk_courses["module"] = "TSK"
    tsk_courses["full_module_name"] = "Modul Freie Wahlfächer und Transferable Skills"
    tsk_courses = tsk_courses[MODULE_COLUMNS]
    return tsk_courses, driver


def clean_curriculum(curriculum: pd.DataFrame, duplicate_columns: list[str]) -> pd.DataFrame:
    cleaned = merge_years(curriculum)
    cleaned = remove_canceled_courses(cleaned)
    cleaned = cleaned.drop_duplicates(
        subset=cleaned.columns.difference(duplicate_columns),
        keep="last",
    )
    cleaned = cleaned.dropna(how="all")
    return cleaned.reset_index(drop=True)
