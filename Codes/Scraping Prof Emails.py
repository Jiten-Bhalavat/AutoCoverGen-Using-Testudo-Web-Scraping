import json
import os
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProfessorEmailScraper:
    def __init__(self, search_url, input_file, output_file):
        """Initialize the scraper with URL, input and output files."""
        self.search_url = search_url
        self.input_file = input_file
        self.output_file = output_file
        self.driver = None
        # Set up Chrome options
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")  # Run in headless mode
        self.chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
        self.chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource issues in containerized environments

    def setup_driver(self):
        """Sets up the WebDriver for Chrome."""
        try:
            self.driver = webdriver.Chrome(options=self.chrome_options)
            logger.info("WebDriver successfully set up.")
        except Exception as e:
            logger.error(f"Error setting up WebDriver: {e}")
            raise

    def get_professor_email(self, prof_name):
        """Searches for a professor's email on the UMD search page and returns it."""
        self.driver.get(self.search_url)
        try:
            search_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "basicSearchInput"))
            )
            search_box.clear()
            search_box.send_keys(prof_name)
            search_box.send_keys(Keys.RETURN)

            email_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'mailto:') and contains(text(), '@umd.edu')]"))
            )
            email = email_element.text
            logger.info(f"Found email for professor {prof_name}: {email}")
            return email

        except (TimeoutException, NoSuchElementException):
            logger.warning(f"No email found for {prof_name}")
            return None

    def process_professor_emails(self):
        """Processes the JSON data to find emails of professors listed in the courses."""
        if not os.path.exists(self.input_file):
            logger.error(f"Input file {self.input_file} does not exist.")
            return
        
        try:
            with open(self.input_file, 'r') as f:
                data = json.load(f)
            logger.info(f"Successfully loaded data from {self.input_file}")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from {self.input_file}: {e}")
            return

        results = []

        # Process each course
        for course in data:
            course_id = course.get("course_id")
            course_title = course.get("course_title")
            professors = course.get("professors", [])
            
            course_info = {
                "course_id": course_id,
                "course_title": course_title,
                "emails": []
            }
            
            for prof in professors:
                if "TBA" in prof:
                    logger.info(f"Skipping 'TBA' for course {course_id}")
                    continue

                email = self.get_professor_email(prof)
                if email:
                    course_info["emails"].append({"name": prof, "email": email})
            
            results.append(course_info)

        # Write the results to the output file
        try:
            with open(self.output_file, 'w') as outfile:
                json.dump(results, outfile, indent=4)
            logger.info(f"Emails saved to {self.output_file}")
        except IOError as e:
            logger.error(f"Error saving data to {self.output_file}: {e}")

    def close_driver(self):
        """Closes the WebDriver."""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver closed.")

def main():
    # Define file paths and URL
    search_url = "https://identity.umd.edu/search"
    input_json_file = "Data/Outputs/course_data.json"  # Replace with your input JSON file
    output_json_file = "Data/Outputs/professors_emails.json"  # Replace with your output JSON file

    # Create instance of ProfessorEmailScraper
    scraper = ProfessorEmailScraper(search_url, input_json_file, output_json_file)
    
    # Set up WebDriver, process emails, and clean up
    try:
        scraper.setup_driver()
        scraper.process_professor_emails()
    finally:
        scraper.close_driver()

if __name__ == "__main__":
    main()
