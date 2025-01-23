# driver_utils.py
import logging
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)

def init_driver():
    """
    Initialize a Chrome WebDriver with "stealth" options.
    """
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Add regular browser features
        options.add_argument('--start-maximized')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--enable-javascript')

        # Use a custom user agent
        options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
             AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 \
             Safari/537.36'
        )

        logger.info("Initializing Chrome WebDriver with stealth options...")
        driver = webdriver.Chrome(options=options)

        # Execute CDP command to prevent detection
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            '''
        })
        return driver
    except WebDriverException as e:
        logger.error(f"Error: Unable to initialize WebDriver. Details: {str(e)}")
        raise e

def check_website_accessibility(url):
    """
    Simple check to see if the URL is returning a 200 status code.
    """
    try:
        logger.info(f"Checking website accessibility for: {url}")
        response = requests.get(url, verify=False, timeout=5)
        logger.info(f"Website response status code: {response.status_code}")
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        logger.error(f"Error checking website: {str(e)}")
        return False

def wait_for_page_load(driver, timeout=5):
    """
    Waits until the document.readyState == 'complete'.
    """
    try:
        logger.info("Waiting for page to load completely...")
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        # Additional small wait to let JS finalize
        time.sleep(2)
        logger.info("Page load complete.")
        return True
    except Exception as e:
        logger.error(f"Error waiting for page load: {str(e)}")
        return False

def wait_for_element(driver, locator_type, locator_value, timeout=10, clickable=False):
    """
    Wait for an element to be present and optionally clickable.
    Returns the element if found, otherwise None.
    """
    try:
        if clickable:
            element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((locator_type, locator_value))
            )
        else:
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((locator_type, locator_value))
            )
        return element
    except TimeoutException:
        logger.warning(f"Timeout waiting for element: {locator_type}={locator_value}")
        return None
    except Exception as e:
        logger.error(f"Error finding element {locator_type}={locator_value}: {str(e)}")
        return None
