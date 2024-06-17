import os
import shutil
import time
import requests
from loguru import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from lxml import html
from selenium.common.exceptions import TimeoutException, WebDriverException

def initialize_driver():
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        return driver
    except WebDriverException as e:
        logger.error(f"Error initializing WebDriver: {e}")
        raise

def get_user_season_input():
    season_input = input("Enter the season (e.g., 'Fall 2024 Ready-to-Wear'): ").strip()
    season_url_part = season_input.replace(" ", "-").lower()
    return season_url_part, season_input

def create_season_directory(season_name):
    if not os.path.exists(season_name):
        os.makedirs(season_name)
        logger.info(f"Directory {season_name} created.")
    else:
        logger.info(f"Directory {season_name} already exists.")

def download_image(image_url, season_name, image_number):
    try:
        response = requests.get(image_url, stream=True)
        filename = os.path.join(season_name, f"{image_number}.jpg")
        with open(filename, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        logger.info(f"Image saved: {filename}")
    except requests.RequestException as e:
        logger.error(f"Failed to download image {image_url}: {e}")
    finally:
        response.close()

def find_and_click_load_more_button(driver):
    try:
        load_more_button = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(), 'Load More')]]"))
        )
        load_more_button.click()
        logger.info("Clicked 'Load More' button.")
        return True
    except TimeoutException:
        logger.info("Load More button not found.")
        return False

def scroll_incrementally(driver, scroll_increment=300, max_attempts=100):
    attempts = 0
    content_loaded = False

    while attempts < max_attempts and not content_loaded:
        driver.execute_script(f"window.scrollBy(0, {scroll_increment});")
        time.sleep(0.5)

        if find_and_click_load_more_button(driver):
            logger.info("Waiting for content to load.")
            time.sleep(5)
            content_loaded = True
        else:
            attempts += 1

        if attempts >= max_attempts:
            logger.info("Reached maximum attempts or end of content.")
            break

    if content_loaded:
        logger.info("Content loaded successfully.")
    else:
        logger.info("Could not find more content to load.")

def main():
    driver = None
    try:
        driver = initialize_driver()
        user_season_url, season_name = get_user_season_input()
        collection_url = f"https://www.vogue.com/fashion-shows/{user_season_url}/yohji-yamamoto"
        driver.get(collection_url)
        logger.info(f"Collection URL: {collection_url}")

        script = """
        var paywall = document.querySelector('.PersistentBottomWrapper-eddooY.bIieWF.persistent-bottom');
        if (paywall) {
            paywall.style.display = 'none';
        }
        """
        driver.execute_script(script)
        logger.info("Paywall disabled.")

        scroll_incrementally(driver)

        page_source = driver.page_source
        tree = html.fromstring(page_source)
        image_elements = tree.xpath('//*[@id="gallery-collection"]/div/div[1]/div/div/a/figure/span/picture/img')
        image_urls = [element.get('src') for element in image_elements]
        logger.info(f"Found {len(image_urls)} images to download.")

        create_season_directory(season_name)

        for idx, url in enumerate(image_urls, start=1):
            download_image(url, season_name, idx)

        logger.success(f"Downloaded {len(image_urls)} images for {season_name}.")

    except Exception as e:
        logger.error(f"An error occurred: {e}")

    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()
