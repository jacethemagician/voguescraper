import os
import json

# Set TensorFlow logging level to only show errors
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import shutil
import time

import requests
from lxml import html
from loguru import logger
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from tqdm import tqdm


def get_user_input():
    """Get season, brand, and scroll option input from the user."""
    print("\nCollection Information")
    season_input = input("Enter season name (e.g. Fall 2024 Ready-to-Wear): ").strip()
    brand_input = input("Enter designer/brand name (e.g. Yohji Yamamoto): ").strip()

    processed_brand = brand_input.replace(" ", "-").lower()
    processed_season = season_input.replace(" ", "-").lower()

    scroll_choice = input("\nLoad all images? (yes/no): ").strip().lower()

    return processed_season, season_input, processed_brand, scroll_choice == "yes"


def get_proxy_settings():
    """Get proxy configuration from user or environment variables."""
    env_proxy = os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy")
    if env_proxy:
        use_env_proxy = input(
            f"Found system proxy {env_proxy}. Use it? (yes/no): "
        ).lower()
        if use_env_proxy == "yes":
            return env_proxy

    print("\nProxy Configuration (Leave blank if not using proxy)")
    proxy_ip = input("Enter proxy IP address (e.g. 192.168.1.100): ").strip()
    proxy_port = input("Enter proxy port (e.g. 8080): ").strip()

    if proxy_ip and proxy_port:
        return f"http://{proxy_ip}:{proxy_port}"
    return ""


def initialize_driver():
    """Initialize the Selenium WebDriver with proxy settings."""
    try:
        proxy_url = get_proxy_settings()

        # Set proxy for ChromeDriverManager
        if proxy_url:
            os.environ["HTTP_PROXY"] = proxy_url
            os.environ["HTTPS_PROXY"] = proxy_url

        service = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()

        if proxy_url:
            options.add_argument(f"--proxy-server={proxy_url}")
            logger.info(f"Using proxy server: {proxy_url}")

            # Test proxy connection
            test_driver = webdriver.Chrome(service=service, options=options)
            try:
                test_driver.get("http://httpbin.org/ip")
                public_ip = json.loads(
                    test_driver.find_element(By.TAG_NAME, "pre").text
                )["origin"]
                logger.success(f"Proxy connection successful. Public IP: {public_ip}")
                test_driver.quit()
            except Exception as e:
                logger.error(f"Proxy test failed: {str(e)}")
                test_driver.quit()
                raise

        # Main driver instance
        driver = webdriver.Chrome(service=service, options=options)
        driver.get("https://www.google.com")
        logger.success("Internet connection test successful")
        return driver

    except WebDriverException as e:
        logger.error(f"Connection failed: {e.msg.split('(')[0]}")
        if "ERR_PROXY_CONNECTION_FAILED" in str(e):
            logger.error(
                "Common fixes: 1) Update ChromeDriver 2) Check proxy format 3) Disable VPN"
            )
        raise


def create_season_directory(brand_name, season_name):
    """Create directory for the brand and season if it doesn't exist."""
    directory_name = f"{brand_name}_{season_name}"
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)
        logger.success(f"Directory {directory_name} created.")
    else:
        logger.info(f"Directory {directory_name} already exists.")
    return directory_name


def download_image(image_url, directory_name, image_number):
    """Download an image from the provided URL."""
    try:
        response = requests.get(image_url, stream=True)
        filename = os.path.join(directory_name, f"{image_number}.jpg")
        with open(filename, "wb") as out_file:
            shutil.copyfileobj(response.raw, out_file)
    except requests.RequestException as e:
        logger.error(f"Failed to download image {image_url}: {e}")
    finally:
        response.close()


def find_and_click_load_more_button(driver):
    """Find and click the 'Load More' button on the page."""
    try:
        load_more_button = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[.//span[contains(text(), 'Load More')]]")
            )
        )
        load_more_button.click()
        logger.info("Clicked 'Load More' button.")
        return True
    except TimeoutException:
        logger.info("Load More button not found.")
        return False


def scroll_incrementally(driver, scroll_increment=300, max_attempts=100):
    """Scroll incrementally to load more content."""
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
        logger.success("Content loaded successfully.")
    else:
        logger.warning("Could not find more content to load.")


def main():
    """Main function to scrape images from Vogue fashion show."""
    driver = None
    try:
        # Initialize driver and test connection first
        driver = initialize_driver()

        # Only prompt for input after successful connection
        user_season_url, season_name, brand_name, should_scroll = get_user_input()

        collection_url = (
            f"https://www.vogue.com/fashion-shows/{user_season_url}/{brand_name}"
        )
        driver.get(collection_url)
        logger.info(f"Collection URL: {collection_url}")

        # Disable paywall
        script = """
        var paywall = document.querySelector('.PersistentBottomWrapper-eddooY.bIieWF.persistent-bottom');
        if (paywall) {
            paywall.style.display = 'none';
        }
        """
        driver.execute_script(script)
        logger.info("Paywall disabled.")

        # Scroll incrementally if the user chooses to
        if should_scroll:
            scroll_incrementally(driver)

        page_source = driver.page_source
        tree = html.fromstring(page_source)
        image_elements = tree.xpath(
            '//*[@id="gallery-collection"]/div/div[1]/div/div/a/figure/span/picture/img'
        )
        image_urls = [element.get("src") for element in image_elements]
        logger.info(f"Found {len(image_urls)} images to download.")

        directory_name = create_season_directory(brand_name, season_name)

        for idx, url in enumerate(tqdm(image_urls, desc="Downloading images"), start=1):
            download_image(url, directory_name, idx)

        logger.success(f"Downloaded {len(image_urls)} images for {directory_name}.")

    except Exception as e:
        logger.error(f"An error occurred: {e}")

    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    main()
