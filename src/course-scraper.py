import requests
from bs4 import BeautifulSoup
import json
import os
import time
from typing import List, Dict
import logging
from urllib.parse import urljoin

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AVCourseScraper:
    def __init__(self):
        self.base_url = "https://courses.analyticsvidhya.com/courses/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def collect_course_links(self) -> List[str]:
        """Collect all course links from the main page"""
        logger.info("Collecting course links...")
        try:
            response = requests.get(self.base_url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            course_links = []
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                if '/courses/' in href:
                    full_link = urljoin("https://courses.analyticsvidhya.com", href)
                    if full_link not in course_links:
                        course_links.append(full_link)
                        logger.info(f"Found course link: {full_link}")
            
            return course_links
            
        except Exception as e:
            logger.error(f"Error collecting course links: {e}")
            return []

    def extract_course_details(self, url: str) -> Dict:
        """Extract details from a course page"""
        try:
            logger.info(f"Extracting details from: {url}")
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract course details
            details = {
                'url': url,
                'title': '',
                'description': '',
                'curriculum': [],
                'instructor': '',
                'price': '',
                'skills': []
            }
            
            # Extract title
            title_elem = soup.find('h1', class_='course-title')
            if title_elem:
                details['title'] = title_elem.text.strip()
            
            # Extract description
            desc_elem = soup.find('div', class_='course-description')
            if desc_elem:
                details['description'] = desc_elem.text.strip()
            
            # Extract curriculum
            curriculum_items = soup.find_all('div', class_='curriculum-item')
            details['curriculum'] = [item.text.strip() for item in curriculum_items]
            
            # Extract instructor
            instructor_elem = soup.find('div', class_='instructor-name')
            if instructor_elem:
                details['instructor'] = instructor_elem.text.strip()
            
            # Extract price
            price_elem = soup.find('div', class_='course-price')
            if price_elem:
                details['price'] = price_elem.text.strip()
            
            return details
            
        except Exception as e:
            logger.error(f"Error extracting details from {url}: {e}")
            return None

    def scrape_all_courses(self) -> List[Dict]:
        """Main method to scrape all courses"""
        # Create data directory
        os.makedirs('data', exist_ok=True)
        
        # Collect all course links
        course_links = self.collect_course_links()
        logger.info(f"Found {len(course_links)} course links")
        
        # Save links to file
        with open("data/av-free-course-data.txt", "w") as file:
            for link in course_links:
                file.write(f"{link}\n")
        
        # Extract details from each course
        courses_data = []
        for link in course_links:
            course_details = self.extract_course_details(link)
            if course_details:
                courses_data.append(course_details)
            time.sleep(1)  # Polite delay between requests
        
        # Save detailed data to JSON
        with open("data/courses_data.json", "w", encoding='utf-8') as file:
            json.dump(courses_data, file, indent=2, ensure_ascii=False)
        
        logger.info(f"Successfully scraped {len(courses_data)} courses")
        return courses_data

def main():
    scraper = AVCourseScraper()
    scraper.scrape_all_courses()

if __name__ == "__main__":
    main()