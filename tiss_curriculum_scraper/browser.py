import logging

import chromedriver_autoinstaller
from selenium import webdriver

LOGGER = logging.getLogger(__name__)


def initiate_chrome_driver() -> webdriver.Chrome:
    """Initiate a headless Chrome WebDriver."""
    chromedriver_autoinstaller.install()

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

    LOGGER.info("Starting headless Chrome driver")
    return webdriver.Chrome(options=chrome_options)
