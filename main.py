import logging
from config import URL, BOOKING_DETAILS, USER_DETAILS_LIST
from driver_utils import init_driver, wait_for_page_load
from booking import process_booking

def configure_logging():
    """
    Sets up the logging format and level.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%H:%M:%S"
    )
    return logging.getLogger(__name__)

def main():
    logger = configure_logging()

    for user_details in USER_DETAILS_LIST:
        # Only proceed if Book is Y
        if user_details.get("Book") == "Y":
            logger.info(f"Starting booking for vehicle: {user_details['vehicle_reg']}")
            driver = None

            try:
                driver = init_driver()
                logger.info(f"Accessing URL: {URL}")
                driver.get(URL)

                if not wait_for_page_load(driver):
                    raise Exception("Page did not load fully.")

                if not process_booking(driver, BOOKING_DETAILS, user_details):
                    raise Exception(f"Failed booking for {user_details['vehicle_reg']}")

                logger.info(f"Booking completed for {user_details['vehicle_reg']}.")
            
            except Exception as e:
                logger.error(f"Error for {user_details['vehicle_reg']}: {e}", exc_info=True)
            
            finally:
                if driver:
                    driver.quit()
                logger.info(f"Driver closed for {user_details['vehicle_reg']}.\n")
        else:
            logger.info(f"Skipping {user_details['vehicle_reg']} because Book=N.")

if __name__ == "__main__":
    main()
