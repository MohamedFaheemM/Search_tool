import os
import json
import logging
import time
from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalyticsVidhyaScraper:
    def __init__(self):
        self.base_url = "https://courses.analyticsvidhya.com/collections/courses"
        self.setup_driver()

    def setup_driver(self):
        """Setup Selenium WebDriver with enhanced Chrome options"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)

    def get_page_content(self, url: str) -> bool:
        """Load page and ensure content is loaded"""
        try:
            self.driver.get(url)
            # Wait for the course container to load
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "collections-products")))
            
            # Scroll to load all content
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            while True:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                
            return True
        except Exception as e:
            logger.error(f"Error loading page: {e}")
            return False

    def extract_course_links(self) -> List[Dict]:
        """Extract course information"""
        courses_info = []
        try:
            # Find all course containers
            course_containers = self.driver.find_elements(By.CSS_SELECTOR, ".collections-products .product-item")
            logger.info(f"Found {len(course_containers)} course containers")
            
            for container in course_containers:
                try:
                    course_info = {}
                    
                    # Extract course title and URL
                    title_link = container.find_element(By.CSS_SELECTOR, "a.product-title")
                    course_info['title'] = title_link.text.strip()
                    course_info['url'] = title_link.get_attribute('href')
                    
                    # Extract price information
                    try:
                        price_elem = container.find_element(By.CSS_SELECTOR, ".product-price-value")
                        course_info['price'] = price_elem.text.strip()
                    except:
                        course_info['price'] = "N/A"
                        
                    # Extract thumbnail
                    try:
                        img_elem = container.find_element(By.CSS_SELECTOR, "img.product-thumbnail")
                        course_info['thumbnail'] = img_elem.get_attribute('src')
                    except:
                        course_info['thumbnail'] = None
                        
                    # Extract description if available
                    try:
                        desc_elem = container.find_element(By.CSS_SELECTOR, ".product-description")
                        course_info['description'] = desc_elem.text.strip()
                    except:
                        course_info['description'] = ""
                    
                    logger.info(f"Found course: {course_info['title']}")
                    courses_info.append(course_info)
                    
                except Exception as e:
                    logger.error(f"Error processing course container: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error extracting courses: {e}")
            
        return courses_info

    def get_course_details(self, url: str) -> Dict:
        """Get detailed information from course page"""
        try:
            self.driver.get(url)
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "product-page")))
            
            details = {}
            
            # Extract full description
            try:
                desc_elem = self.driver.find_element(By.CSS_SELECTOR, ".product-description")
                details['full_description'] = desc_elem.text.strip()
            except:
                details['full_description'] = ""
                
            # Extract curriculum if available
            try:
                curriculum_items = self.driver.find_elements(By.CSS_SELECTOR, ".curriculum-item")
                details['curriculum'] = [item.text.strip() for item in curriculum_items]
            except:
                details['curriculum'] = []
                
            return details
            
        except Exception as e:
            logger.error(f"Error getting course details: {e}")
            return {}

    def scrape_all_courses(self) -> List[Dict]:
        """Main method to scrape all courses"""
        logger.info("Starting course scraping...")
        
        if not self.get_page_content(self.base_url):
            logger.error("Failed to load the main page")
            return []

        # Get basic course information
        courses_info = self.extract_course_links()
        logger.info(f"Found {len(courses_info)} courses")

        # Get detailed information for each course
        detailed_courses = []
        for course in courses_info:
            logger.info(f"Getting details for: {course['title']}")
            details = self.get_course_details(course['url'])
            course.update(details)
            detailed_courses.append(course)
            time.sleep(1)  # Be nice to the server

        return detailed_courses

    def cleanup(self):
        """Close the browser"""
        if hasattr(self, 'driver'):
            self.driver.quit()

def main():
    os.makedirs('data', exist_ok=True)
    scraper = None
    
    try:
        scraper = AnalyticsVidhyaScraper()
        courses = scraper.scrape_all_courses()
        
        if courses:
            with open('data/courses.json', 'w', encoding='utf-8') as f:
                json.dump(courses, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(courses)} courses to data/courses.json")
        else:
            logger.error("No courses were found to save")
            
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        if scraper:
            scraper.cleanup()

if __name__ == "__main__":
    main()