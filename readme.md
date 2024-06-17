# Vogue Fashion Show Image Scraper

**Latest Commit:** ✅ _2024-06-17_

This project is a Python script for downloading images from Vogue fashion shows. It uses Selenium to automate the web browser, fetch the images, and save them locally. This README provides an overview of the script, its usage, and its dependencies.

Currently only runs for Yohji Yamamoto because I'm a Yoji fan.

## Table of Contents
- [Features](#features)
- [Requirements](#requirements)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)
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


## Usage

1. **Run the Script:**
   ```sh
   python vogue_se.py
   ```

2. **Enter the Fashion Show Season:**
   When prompted, enter the season name (e.g., `Fall 2024 Ready-to-Wear`).

3. **Wait for Images to Download:**
   The script will navigate to the specified season's page, scroll to load all images, and download them into a directory named after the season.


## Troubleshooting

1. **ChromeDriver Issues:**
   Ensure you have the latest version of ChromeDriver compatible with your Chrome browser. This is managed by `webdriver_manager`, but manual checks can help.

2. **Website Changes:**
   Vogue's website structure might change, affecting the script. Inspect the elements and update the XPath selectors accordingly.

3. **Slow Performance:**
   Increase the sleep intervals in the `scroll_incrementally` function to allow more time for content to load.

4. **Paywall Issues:**
   The script includes a basic paywall bypass that might not work for all cases. Further tweaks might be necessary based on the site's updates.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Legal Disclaimer

This project is not affiliated with, endorsed by, or in any way associated with Vogue or its parent company. The content and images accessed through this script are the property of Vogue and are used for educational and non-commercial purposes only. 

By using this script, you agree to use it responsibly and acknowledge that the developers of this project are not liable for any misuse. If the usage of this script is found to harm the web integrity or violate the terms of service of Vogue, the developers will take immediate action to remove or modify the script as necessary.

---