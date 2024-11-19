import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import logging
import os
from selenium.webdriver.chrome.options import Options

class CourseScraper:
    def __init__(self, output_dir="Data/Outputs"):
        self.base_url = ("https://app.testudo.umd.edu/soc/search?courseId={course}&termId={term}&_openSectionsOnly=on&creditCompare=&credits=&courseLevelFilter={level}&instructor=&_facetoface=on&_blended=on&_online=on&courseStartCompare=&courseStartHour=&courseStartMin=&courseStartAM=&courseEndHour=&courseEndMin=&courseEndAM=&teachingCenter=ALL&_classDay1=on&_classDay2=on&_classDay3=on&_classDay4=on&_classDay5=on"
        )
        # self.driver_path = driver_path or "chromedriver"  # Default to chromedriver in PATH
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)  # Ensure output directory exists
        self.driver = None
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
        # Set up Chrome options
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")  # Run in headless mode
        self.chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
        self.chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource issues in containerized environments

    def get_user_input(self):
        # Get course input
        courses = {"1": "DATA", "2": "MSML"}
        print("Select Course:")
        for k, v in courses.items():
            print(f"{k}: {v}")
        course_choice = input("Enter Course Number: ")
        course = courses.get(course_choice, "DATA")  # Default to DATA if input is invalid

        # Get term input
        terms = {
            "Summer 2024": "202405",
            "Fall 2024": "202408",
            "Winter 2025": "202412",
            "Spring 2025": "202501"
        }
        print("\nSelect Term:")
        for k, v in terms.items():
            print(f"{k}: {v}")
        term_choice = input("Enter Term Name: ")
        term_id = terms.get(term_choice, "202501")  # Default to Winter 2025 if input is invalid

        # Get level input
        levels = {"1": "ALL", "2": "undergraduate", "3": "Graduate"}
        print("\nSelect Level:")
        for k, v in levels.items():
            print(f"{k}: {v}")
        level_choice = input("Enter Level Number: ")
        level = levels.get(level_choice, "ALL")  # Default to ALL if input is invalid

        return course, term_id, level

    def scrape_course_data(self, course, term_id, level):
        # Construct URL with user-selected parameters
        url = self.base_url.format(course=course, term=term_id, level=level)

        # Initialize the driver
        self.driver = webdriver.Chrome(options=self.chrome_options)
        logging.info(f"Fetching data from {url}")
        self.driver.get(url)
        time.sleep(2)  # Wait for page to load

        # Click "Show All Sections" to expand professor details if necessary
        try:
            show_all_sections_button = self.driver.find_element(By.ID, "show-all-sections-button")
            show_all_sections_button.click()
            time.sleep(2)
        except NoSuchElementException:
            logging.warning("No 'Show All Sections' button found or failed to expand sections.")

        # Parse HTML content
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        course_data = []

        # Extract course details
        course_divs = soup.select('.course')
        for course_div in course_divs:
            course_id = course_div.select_one(".course-id").text.strip()
            course_title = course_div.select_one(".course-title").text.strip()

            # Extract course description
            description_divs = course_div.select('.approved-course-text')
            course_description = "No description available"
            for desc in description_divs:
                if not desc.find("strong"):
                    course_description = desc.text.strip()
                    break

            # Extract professor and section details
            professor_set = set()  # To track unique professors
            sections = course_div.select(".section")
            for section in sections:
                prof_name_element = section.select_one(".section-instructor")
                if prof_name_element:
                    professor_set.add(prof_name_element.text.strip())

            course_data.append({
                "course_id": course_id,
                "course_title": course_title,
                "description": course_description,
                "professors": list(professor_set)  # Convert set to list
            })

        return course_data

    def save_to_json(self, data, filename="course_data.json"):
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
        logging.info(f"Data saved to {filepath}")

    def run(self):
        course, term_id, level = self.get_user_input()
        course_data = self.scrape_course_data(course, term_id, level)
        self.save_to_json(course_data)
        self.driver.quit()


if __name__ == "__main__":
    scraper = CourseScraper()
    scraper.run()
