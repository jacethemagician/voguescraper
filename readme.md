# Vogue Fashion Show Image Downloader

This project is a Python script for downloading images from Vogue fashion shows. It uses Selenium to automate the web browser, fetch the images, and save them locally. This README provides an overview of the script, its usage, and its dependencies.

## Table of Contents
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Code Explanation](#code-explanation)
  - [initialize_driver](#initialize_driver)
  - [get_user_season_input](#get_user_season_input)
  - [create_season_directory](#create_season_directory)
  - [download_image](#download_image)
  - [find_and_click_load_more_button](#find_and_click_load_more_button)
  - [scroll_incrementally](#scroll_incrementally)
  - [main](#main)
- [Logging](#logging)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Features
- **Automated Browsing:** Uses Selenium WebDriver to navigate and interact with the Vogue website.
- **Image Downloading:** Downloads images from a specified fashion show season.
- **Directory Management:** Creates and manages directories for saving images.
- **Paywall Handling:** Attempts to disable paywalls on the Vogue website.
- **Incremental Scrolling:** Scrolls the page incrementally to load more content.

## Requirements
- Python 3.7+
- Google Chrome browser
- ChromeDriver
- The following Python libraries:
  - requests
  - shutil
  - loguru
  - selenium
  - webdriver_manager
  - lxml

## Installation

1. **Clone the Repository:**
   ```sh
   git clone https://github.com/yourusername/vogue-image-downloader.git
   cd vogue-image-downloader
   ```

2. **Install Dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

3. **Ensure ChromeDriver is installed:**
   ChromeDriver will be managed automatically by `webdriver_manager`.

## Usage

1. **Run the Script:**
   ```sh
   python vogue_downloader.py
   ```

2. **Enter the Fashion Show Season:**
   When prompted, enter the season name (e.g., `Fall 2024 Ready-to-Wear`).

3. **Wait for Images to Download:**
   The script will navigate to the specified season's page, scroll to load all images, and download them into a directory named after the season.

## Code Explanation

### `initialize_driver`

Initializes the Chrome WebDriver using `webdriver_manager` to manage the ChromeDriver installation.

```python
def initialize_driver():
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        return driver
    except WebDriverException as e:
        logger.error(f"Error initializing WebDriver: {e}")
        raise
```

### `get_user_season_input`

Prompts the user for the season and formats it for the URL.

```python
def get_user_season_input():
    season_input = input("Enter the season (e.g., 'Fall 2024 Ready-to-Wear'): ").strip()
    season_url_part = season_input.replace(" ", "-").lower()
    return season_url_part, season_input
```

### `create_season_directory`

Creates a directory for the season if it doesn't exist.

```python
def create_season_directory(season_name):
    if not os.path.exists(season_name):
        os.makedirs(season_name)
        logger.info(f"Directory {season_name} created.")
    else:
        logger.info(f"Directory {season_name} already exists.")
```

### `download_image`

Downloads an image and saves it to the specified directory.

```python
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
```

### `find_and_click_load_more_button`

Finds and clicks the "Load More" button to load additional images.

```python
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
```

### `scroll_incrementally`

Scrolls the page incrementally to load content and clicks "Load More" if available.

```python
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
```

### `main`

The main function that ties everything together.

```python
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
```

## Logging

The script uses the `loguru` library for logging various stages of the execution, such as:
- Initialization of the WebDriver.
- User inputs.
- Directory creation.
- Image downloading.
- Handling of paywalls.
- Incremental scrolling.
- Errors and exceptions.

## Troubleshooting

1. **ChromeDriver Issues:**
   Ensure you have the latest version of ChromeDriver compatible with your Chrome browser. This is managed by `webdriver_manager`, but manual checks can help.

2. **Website Changes:**
   Vogue's website structure might change, affecting the script. Inspect the elements and update the XPath selectors accordingly.

3. **Slow Performance:**
   Increase the sleep intervals in the `scroll_incrementally` function to allow more time for content to load.

4. **Paywall Issues:**
   The script includes a basic paywall bypass that might not work for all cases. Further tweaks might be necessary based on the site's updates.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests with improvements or bug fixes.

1. **Fork the Repository:**
   Click the "Fork" button on the top-right corner of this page to create a copy of the repository in your GitHub account.

2. **Clone the Fork:**
   ```sh
   git clone https://github.com/yourusername/vogue-image-downloader.git
   cd vogue-image-downloader
   ```

3. **Create a Branch:**
   ```sh
   git checkout -b feature-branch
   ```

4. **Make Your Changes and Commit:**
   ```sh
   git commit -am 'Add new feature'
   ```

5. **Push to the Branch:**
   ```sh
   git push origin feature-branch
   ```

6. **Open a Pull Request:**
   Navigate to the original repository and click the "New Pull Request" button to submit your changes for review.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Feel free to customize this README to better fit your needs and provide any additional information specific to your project.