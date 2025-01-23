import logging
from config import URL, BOOKING_DETAILS, USER_DETAILS_LIST
from driver_utils import init_driver, wait_for_page_load
from booking import validate_booking_time, select_dates, process_booking

def configure_logging():
    """
    Sets up the logging format and level.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%H:%M:%S"
    )
    logger = logging.getLogger(__name__)
    return logger

def main():
    logger = configure_logging()

    for user_details in USER_DETAILS_LIST:
        logger.info(f"Starting booking process for vehicle: {user_details['vehicle_reg']}")
        driver = None

        try:
            # Validate the booking timeframe
            validate_booking_time()

            # Initialize the driver and load the URL
            driver = init_driver()
            logger.info(f"Accessing URL: {URL}")
            driver.get(URL)

            if not wait_for_page_load(driver):
                raise Exception("Page did not load completely.")

            # Process the booking for the current user
            if not process_booking(driver, BOOKING_DETAILS, user_details):
                raise Exception(f"Failed to complete booking for {user_details['vehicle_reg']}")

            logger.info(f"Booking flow completed for {user_details['vehicle_reg']}.")

        except Exception as e:
            logger.error(f"Critical error occurred for {user_details['vehicle_reg']}: {e}", exc_info=True)
        finally:
            if driver:
                driver.quit()
            logger.info(f"Driver closed for vehicle: {user_details['vehicle_reg']}.\n\n")

if __name__ == "__main__":
    main()
