import os
import shutil
from loguru import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from lxml import html
import requests
import time

# Initialize Selenium WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

def get_user_season_input():
    season_input = input("Enter the season (e.g., 'Fall 2024 Ready-to-Wear'): ").strip()
    season_url_part = season_input.replace(" ", "-").lower()
    return season_url_part, season_input

def create_season_directory(season_name):
    if not os.path.exists(season_name):
        os.makedirs(season_name)
        logger.info(f"Directory {season_name} created.")

def download_image(image_url, season_name, image_number):
    try:
        response = requests.get(image_url, stream=True)
        filename = os.path.join(season_name, f"{image_number}.jpg")
        with open(filename, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        logger.info(f"Image saved: {filename}")
    finally:
        response.close()

from selenium.common.exceptions import TimeoutException

def find_and_click_load_more_button():
    try:
        # Use XPath to find a button containing specific text
        load_more_button = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(), 'Load More')]]"))
        )
        load_more_button.click()
        logger.info("Clicked 'Load More' button based on text.")
        return True
    except TimeoutException:
        logger.info("Load More button not found based on text.")
        return False


def scroll_incrementally(scroll_increment=300, max_attempts=100):
    attempts = 0
    content_loaded = False  # Flag to indicate if content has been loaded

    while attempts < max_attempts and not content_loaded:
        # Scroll by the specified increment
        driver.execute_script(f"window.scrollBy(0, {scroll_increment});")
        time.sleep(0.5)  # Give a moment for the page to adjust after scrolling

        button_clicked = find_and_click_load_more_button()
        if button_clicked:
            logger.info("Successfully clicked 'Load More' button. Waiting for content to load.")
            time.sleep(5)  # Wait for 30 seconds to allow all content to load
            content_loaded = True  # Set flag to true as content has been loaded
        else:
            logger.info("Attempting to find 'Load More' button...")
            attempts += 1

        if attempts >= max_attempts:
            logger.info("Reached maximum attempts or end of content.")

    # After exiting the loop, either all content is loaded or max attempts reached
    if content_loaded:
        logger.info("Content loaded successfully.")
    else:
        logger.info("Could not find more content to load.")


try:
    user_season_url, season_name= get_user_season_input()
    collection_url = f"https://www.vogue.com/fashion-shows/{user_season_url}/yohji-yamamoto"
    driver.get(collection_url)
    logger.info(f"Collection URL: {collection_url}")

    # JavaScript to hide the paywall or any persistent bottom element
    script = """
    var paywall = document.querySelector('.PersistentBottomWrapper-eddooY.bIieWF.persistent-bottom');
    if (paywall) {
        paywall.style.display = 'none';
    }
    """
    # Execute the JavaScript on the current page
    driver.execute_script(script)
    logger.info("Paywall disabled.")

    # Scroll incrementally to find the "Load More" button
    scroll_incrementally()

    page_source = driver.page_source
    tree = html.fromstring(page_source)
    image_elements = tree.xpath('//*[@id="gallery-collection"]/div/div[1]/div/div/a/figure/span/picture/img')
    image_urls = [element.get('src') for element in image_elements]
    logger.info(f"Found {len(image_urls)} images to download.")

    create_season_directory(season_name)

    image_num = 0
    for url in image_urls:
        image_num += 1
        download_image(url, season_name, str(image_num))

    logger.success(f"Downloaded {len(image_urls)} images for {season_name}.")

finally:
    driver.quit()
