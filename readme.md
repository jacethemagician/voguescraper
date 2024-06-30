# Vogue Fashion Show Image Scraper

**✅Latest Commit:** _2024-06-30_

A simple Python script for downloading images from Vogue fashion shows. It uses Selenium to automate the web browser, fetch the images, and save them locally.

## 🚀Features
- **Automated Browsing:** Uses Selenium WebDriver to navigate and interact with the Vogue website.
- **Image Downloading:** Downloads images from a specified fashion show season and brand.
- **Directory Management:** Creates and manages directories for saving images.
- **Paywall Ad Handling:** Attempts to disable the ad banner on the Vogue website.
- **Incremental Scrolling:** Scrolls the page incrementally to load more content, with an option for the user to enable or disable scrolling.

## 📋Requirements
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
  - tqdm

## 💾Installation

1. **Clone the Repository:**
   ```sh
   git clone https://github.com/yourusername/vogue-fashion-show-scraper.git
   cd vogue-fashion-show-scraper
   ```

2. **Install the Required Python Packages:**
   ```sh
   pip install -r requirements.txt
   ```

## 🕹️Usage

1. **Run the Script:**
   ```sh
   python vogue_se.py
   ```
   - A Chrome webpage will pop up. Do not close the page unless the program completes or fails.

2. **Enter the Fashion Show Season:**
   When prompted, enter the season name (e.g., `Fall 2024 Ready-to-Wear`).
   - Pay attention to spaces and format.

3. **Enter the Brand Name:**
   When prompted, enter the brand name (e.g., `yohji-yamamoto`).
   - If unsure, check the brand name on Vogue. The format should be lowercase letters connected with hyphens.

4. **Choose to Scroll or Not:**
   When prompted, enter `yes` to enable scrolling to load more images or `no` to disable scrolling.
   - This parameter controls whether to mimic scrolling on the specific runway webpage. It's almost always `yes`, but in some rare scenarios, it can be `no`. Please try it out.

5. **Wait for Images to Download:**
   The script will navigate to the specified season's page, scroll to load all images (if enabled), and download them into a directory named after the brand and season.
   - The saved directory is named in the format of brand + season (e.g., `yohji-yamamoto_Fall 2024 Ready-to-Wear`).

## ⚠️Troubleshooting

1. **ChromeDriver Issues:**
   Ensure you have the latest version of ChromeDriver compatible with your Chrome browser. This is managed by `webdriver_manager`, but manual checks can help.

2. **Website Changes:**
   Vogue's website structure might change, affecting the script. Further tweaks might be necessary based on the site's updates.

3. **Slow Performance:**
   Increase the sleep intervals in the `scroll_incrementally` function to allow more time for content to load.

## ⚖️License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🛡️Legal Disclaimer

This project is not affiliated with, endorsed by, or in any way associated with Vogue or its parent company. The content and images accessed through this script are the property of Vogue and are used for educational and non-commercial purposes only. 

By using this script, you agree to use it responsibly and acknowledge that the developers of this project are not liable for any misuse. If the usage of this script is found to harm the web integrity or violate the terms of service of Vogue, the developers will take immediate action to remove or modify the script as necessary.