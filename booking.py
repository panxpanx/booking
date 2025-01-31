# booking.py

import logging
import time
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from driver_utils import wait_for_element
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import current_datetime, PARKING_DETAILS, USER_DETAILS_LIST

logger = logging.getLogger(__name__)

def retry_parking_selection(driver):
    """
    Retry selecting the parking option for up to 30 minutes if sold out.
    """
    logger.info("Retrying Standard Parking selection for up to 30 minutes...")
    end_time = datetime.now() + timedelta(minutes=30)
    while datetime.now() < end_time:
        if not check_sold_out(driver):
            logger.info("Standard Parking is now available!")
            return True
        
        logger.info("Standard Parking still sold out. Going back and retrying...")
        driver.back()
        time.sleep(5)
        driver.refresh()
        time.sleep(10)
    
    logger.error("Standard Parking remained sold out after 30 minutes of retrying.")
    return False

def validate_booking_time():
    """
    Validate that the booking meets time restrictions.
    For example, ensure entry date is in the future.
    """
    entry_date_str = PARKING_DETAILS['entry_date']  # "dd/mm/yyyy"
    entry_datetime = datetime.strptime(f"{entry_date_str} 06:00", "%d/%m/%Y %H:%M")

    logger.info(f"Validating booking date: Entry {entry_datetime.date()}, Now {current_datetime.date()}")

    if entry_datetime.date() < current_datetime.date():
        raise ValueError(f"Entry date must be in the future. Current date is {current_datetime.date()}")

    logger.info("Booking date validation passed.")

def select_dates(driver, booking_data):
    """
    Select/Enter the entry and exit dates on the booking page.
    booking_data typically has {entry_date, exit_date, entry_time, exit_time} in YYYY-MM-DD format.
    """
    logger.info("Selecting booking dates from BOOKING_DETAILS...")

    entry_date_input = wait_for_element(driver, By.ID, "entryDate", timeout=5)
    if entry_date_input:
        entry_date_input.clear()
        entry_date_input.send_keys(booking_data["entry_date"])
        logger.info(f"Entered entry date: {booking_data['entry_date']}")

    exit_date_input = wait_for_element(driver, By.ID, "exitDate", timeout=5)
    if exit_date_input:
        exit_date_input.clear()
        exit_date_input.send_keys(booking_data["exit_date"])
        logger.info(f"Entered exit date: {booking_data['exit_date']}")

def fill_parking_details(driver, user_details):
    """
    Attempts to fill out the parking details form and proceed through the booking steps.
    Includes logic for handling "Book Now" button, sold-out checks, etc.
    """
    logger.info("Starting to fill parking details...")

    # Check for immediate error indicating pre-booking not available
    try:
        error_message = wait_for_element(
            driver, By.CSS_SELECTOR, "div.alert.alert-danger p[role='alert']",
            timeout=3
        )
        if error_message and "Pre-booking parking at Unity Place is coming soon" in error_message.text:
            logger.error(f"ERROR: {error_message.text}")
            logger.error("Cannot proceed - pre-booking is not available for the selected dates.")
            return False
    except:
        pass  # no error found, keep going

    time.sleep(5)  # Wait for the form to finish loading

    # Try to set entry/exit dates with JS (some sites need this approach)
    try:
        entry_date_element = wait_for_element(driver, By.ID, "changeEntryDate", timeout=5)
        if entry_date_element:
            driver.execute_script(
                f"arguments[0].value = '{PARKING_DETAILS['entry_date']}'", 
                entry_date_element
            )
            driver.execute_script("arguments[0].dispatchEvent(new Event('change'))", entry_date_element)
            logger.info(f"Entry date set to {PARKING_DETAILS['entry_date']} via JS")

        time.sleep(2)
    
        entry_time_element = wait_for_element(driver, By.ID, "changeEntryTime", timeout=5)
        if entry_time_element:
            driver.execute_script("arguments[0].value = '06:00'", entry_time_element)
            driver.execute_script("arguments[0].dispatchEvent(new Event('change'))", entry_time_element)
            logger.info("Entry time set to 06:00 via JS")

        exit_date_element = wait_for_element(driver, By.ID, "changeExitDate", timeout=5)
        if exit_date_element:
            driver.execute_script(
                f"arguments[0].value = '{PARKING_DETAILS['exit_date']}'", 
                exit_date_element
            )
            driver.execute_script("arguments[0].dispatchEvent(new Event('change'))", exit_date_element)
            logger.info(f"Exit date set to {PARKING_DETAILS['exit_date']} via JS")

    except Exception as e:
        logger.error(f"Could not set entry/exit dates with JS: {str(e)}")
        return False

    time.sleep(2)

    # Click "Book Now" or "Search" button to continue
    if not click_book_now(driver):
        return False

    # Check whether standard parking is sold out
    if check_sold_out(driver):
        # Attempt to book TAP Permit instead
        if not click_tap_permit_booking(driver):
            return False
    else:
        # Not sold out, try standard parking flow
        if not click_standard_parking(driver):
            return False

    logger.info("about to start entering persanal details")
    # Fill personal details
    if not fill_user_details(driver, user_details):
        logger.error(f"FAILED to fill user details for {user_details['vehicle_reg']}.")
        return False

    # Accept T&Cs and finalize the booking
    if not accept_terms_and_finalize(driver, user_details):
        return False

    return True

def click_book_now(driver):
    """
    Tries various selectors to find a "Book Now" button and clicks it.
    """
    logger.info("Looking for a 'Book Now' button...")
    button_selectors = [
        (By.CSS_SELECTOR, "button.btn.btn-primary[type='submit']"),
        (By.CSS_SELECTOR, "input.btn.btn-primary[type='submit']"),
        (By.CSS_SELECTOR, "input[value='Book Now']"),
        (By.CSS_SELECTOR, "button.btn-primary"),
        (By.XPATH, "//button[text()='Book Now']"),
        (By.XPATH, "//input[@value='Book Now']"),
        (By.XPATH, "//button[contains(@class, 'btn-primary')]")
    ]

    for selector_type, selector_value in button_selectors:
        btn = wait_for_element(driver, selector_type, selector_value, timeout=2, clickable=True)
        if btn:
            try:
                btn.click()
                logger.info(f"Clicked 'Book Now' using {selector_type}={selector_value}")
                time.sleep(2)
                return True
            except Exception as e:
                logger.warning(f"Failed to click button {selector_type}={selector_value}: {str(e)}")
    logger.error("Could not find any functioning 'Book Now' button.")
    return False

def check_sold_out(driver):
    """
    Checks if the parking is sold out by looking for 'Sold Out' text.
    Returns True if sold out, else False.
    """
    logger.info("Checking if parking is sold out...")
    try:
        sold_out_elem = driver.find_element(By.CSS_SELECTOR, "div.item__soldout span")
        if sold_out_elem and "Sold Out" in sold_out_elem.text:
            logger.warning("Standard Parking is sold out.")
            return True
    except:
        pass
    logger.info("Parking not sold out. Continuing...")
    return False

def click_tap_permit_booking(driver):
    """
    Attempts to click on the TAP Permit 'Book Now' button.
    """
    """
    logger.info("Trying to select TAP Permit booking...")
    tap_button_selectors = [
        (By.CSS_SELECTOR, "a.btn.btn-primary.btn--submit.item__cta[data-step2-item='418']"),
        (By.CSS_SELECTOR, "a.btn.btn-primary[href*='pid=418']"),
        (By.XPATH, "//a[contains(@class, 'btn-primary') and contains(@href, 'pid=418')]"),
        (By.XPATH, "//a[@data-step2-item='418']")
    ]

    for sel_type, sel_value in tap_button_selectors:
        tap_btn = wait_for_element(driver, sel_type, sel_value, timeout=3, clickable=True)
        if tap_btn:
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", tap_btn)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", tap_btn)
                logger.info("Clicked TAP Permit 'Book Now' button successfully.")
                time.sleep(2)
                return True
            except Exception as e:
                logger.warning(f"Could not click TAP Permit button with {sel_type}={sel_value}: {str(e)}")
    logger.error("Could not find TAP Permit 'Book Now' button.")
    """
    logger.info("Sold out and didn book TAP")
    return False

def click_standard_parking(driver):
    """
    Attempts to click on the Standard Parking 'Book Now' button, if it exists.
    """
    logger.info("Selecting Standard Parking (pid=413)...")
    if retry_parking_selection(driver):
        standard_parking_button = wait_for_element(
            driver,
            By.CSS_SELECTOR,
            "a.btn.btn-primary.btn--submit.item__cta[data-step2-item='413']",
            timeout=5,
            clickable=True
        )
        if standard_parking_button:
            try:
                standard_parking_button.click()
                logger.info("Clicked 'Standard Parking' book button.")
                time.sleep(2)
                return True
            except Exception as e:
                logger.error(f"Failed clicking Standard Parking button: {str(e)}")
        else:
            logger.error("Standard Parking button not found.")
    else:
        logger.error("Could not select Standard Parking after retries.")
    return False

def fill_user_details(driver, user_details):
    """
    Fill in the user details on the form for each vehicle.
    """
    logger.info(f"Filling details for {user_details['vehicle_reg']}...")

    # First Name
    first_name_el = wait_for_element(driver, By.ID, "firstName", timeout=5)
    if first_name_el:
        first_name_el.clear()
        first_name_el.send_keys(user_details["first_name"])
        logger.info(f"Entered first name: {user_details['first_name']}")
        time.sleep(1)

    # Last Name
    last_name_el = wait_for_element(driver, By.ID, "lastName", timeout=5)
    if last_name_el:
        last_name_el.clear()
        last_name_el.send_keys(user_details["last_name"])
        logger.info(f"Entered last name: {user_details['last_name']}")
        time.sleep(1)

    # Email
    email_el = wait_for_element(driver, By.ID, "email", timeout=5)
    if email_el:
        email_el.clear()
        email_el.send_keys(user_details["email"])
        logger.info(f"Entered email: {user_details['email']}")
        time.sleep(1)

    # Vehicle Registration
    vehicle_reg_el = wait_for_element(driver, By.ID, "registration", timeout=5)
    if vehicle_reg_el:
        try:
            vehicle_reg_el.click()
            logger.info("Clicked vehicle registration input field.")
            time.sleep(2)
            vehicle_reg_el.clear()
            time.sleep(1)
            vehicle_reg_el.send_keys(user_details["vehicle_reg"])
            logger.info(f"Entered vehicle reg: {user_details['vehicle_reg']}")
            time.sleep(2)

            # Verify the text that was entered
            entered_text = vehicle_reg_el.get_attribute("value")
            if not entered_text or entered_text != user_details["vehicle_reg"]:
                logger.error("Failed to confirm entered vehicle registration text.")
                return False
            logger.info("Vehicle registration confirmed.")
        except Exception as e:
            logger.error(f"Error filling vehicle registration: {str(e)}")
            return False

    return True

def process_booking(driver, booking_data, user_details):
    """
    Process booking flow for a single vehicle.
    Includes day-of-week toggles so booking occurs only if Book=Y and today's day is Y.
    """
    # 7-day toggles: Monday=0 .. Sunday=6
    weekday_index = datetime.now().weekday()
    weekdays = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

    # If Book='N', skip entirely
    if user_details.get("Book") != "Y":
        logger.info(f"Skipping {user_details['vehicle_reg']} because Book is 'N'.")
        return False

    # Check day-of-week toggle (mon-sun)
    day_key = weekdays[weekday_index]  # e.g. "mon" if Monday
    if user_details.get(day_key, "N") != "Y":
        logger.info(f"Skipping {user_details['vehicle_reg']} because {day_key.upper()} toggle is not 'Y'.")
        return False

    try:
        # Validate booking time
        validate_booking_time()

        # Select dates (entry/exit)
        select_dates(driver, booking_data)

        # Fill in the rest of the parking details (Book Now, user details, etc.)
        if not fill_parking_details(driver, user_details):
            raise Exception("Failed to fill parking details.")

        logger.info("Completed fill_parking_details...")

        # Accept T&Cs and finalize booking
        terms = wait_for_element(driver, By.ID, "terms", timeout=5)
        if terms:
            driver.execute_script("arguments[0].scrollIntoView(true);", terms)
            time.sleep(1)
            terms.click()
            logger.info("Clicked terms and conditions checkbox.")
        else:
            logger.error("Could not find terms checkbox.")
            return False

        book_button = wait_for_element(driver, By.ID, "PaymentFormSubmit", timeout=5, clickable=True)
        if book_button:
            book_button.click()
            logger.info("Clicked 'Book and Pay'.")
        else:
            logger.error("Could not find 'Book and Pay' button.")
            return False

        # Wait for confirmation page
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Confirmation')]"))
            )
        except TimeoutException:
            logger.error("Booking confirmation not received (Timeout).")
            return False

        # Attempt to extract booking reference
        return extract_booking_reference(driver, user_details)

    except Exception as e:
        logger.error(f"Error during booking process: {e}")
        return False

def accept_terms_and_finalize(driver, user_details):
    """
    If you use a separate function for T&Cs, it’s here for backward compatibility.
    Currently, we do T&Cs in process_booking.
    """
    logger.info("accept_terms_and_finalize is not used in process_booking now, but left for reference.")
    return True

def extract_booking_reference(driver, user_details):
    """
    Searches for a booking reference on the confirmation page and writes it to booking_reference.txt.
    """
    logger.info("Looking for booking reference on the confirmation page...")
    possible_xpaths = [
        "//h2[contains(text(), 'Booking Reference:')]",
        "//div[contains(text(), 'Booking Reference:')]",
        "//p[contains(text(), 'Booking Reference:')]"
    ]
    booking_ref = None

    for xpath in possible_xpaths:
        try:
            ref_el = driver.find_element(By.XPATH, xpath)
            if ref_el:
                text_parts = ref_el.text.split("Reference:")
                if len(text_parts) > 1:
                    booking_ref = text_parts[1].strip()
                    break
        except:
            continue

    if booking_ref:
        logger.info(f"Booking confirmed! Reference: {booking_ref}")
        with open("/Users/admin/pip_install/booking_reference.txt", "a") as f:
            f.write(f"Booking Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f" BOOKED FOR {user_details['first_name']}\n")
            f.write(f"Booking Reference: {booking_ref}\n")
        logger.info("Booking reference saved to booking_reference.txt")
        return True
    else:
        logger.error("Could not find booking reference on confirmation page.")
        return False
