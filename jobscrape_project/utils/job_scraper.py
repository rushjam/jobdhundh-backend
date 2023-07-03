from .date_conversion import convert_date_format

import time
from datetime import datetime
import requests
import logging
import hashlib
import json

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import NoSuchElementException
from requests.exceptions import RequestException
from selenium.common.exceptions import WebDriverException

from jobs.models import JobListing, Company, Tag, Category, JobType

# Initialize a logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_hash(job_data):
    job_string = json.dumps(job_data, sort_keys=True)  # Convert the job data to a sorted string
    job_hash = hashlib.md5(job_string.encode())  # Create a hash from the job string
    return job_hash.hexdigest()  # Return the hexadecimal representation of the hash


class JobScraper:
    def __init__(self, driver_path, dynamic=False):
        self.driver_path = driver_path
        self.dynamic = dynamic

        # Define chrome options
        chrome_options = Options()

        # If the dynamic option is set, add the --headless option
        if dynamic:
            chrome_options.add_argument("--headless")

        # Initialize the Chrome driver
        # self.driver = webdriver.Chrome(options=chrome_options)
        self.driver = webdriver.Chrome()

    def __del__(self):
        self.driver.quit()

    def load_website(self, url, load_more_selector=None, infinite_scroll=False, next_page_selector=None, website_config=None, job_type=None, category=None):
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                if self.dynamic:
                    self.driver.get(url)
                    time.sleep(5)

                    # If the page has a "Load More" button, click it until it disappears
                    while load_more_selector and self.load_more(load_more_selector):
                        pass

                    # If the page uses infinite scrolling, scroll to the bottom
                    if infinite_scroll:
                        self.infinite_scroll_page()

                    # Loop to navigate through multiple pages
                    all_job_listings = []
                    job_id = 0

                    while True:
                        html = self.driver.page_source
                        # create soup object only once per page
                        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                        for job_element in soup.select(website_config['job_selector']):
                            job_id += 1
                            all_job_listings.append(self.scrape_job(job_element, website_config, job_id, job_type, category))
                        try:
                            # Break the loop if navigate_next_page() returns False

                            if not self.navigate_next_page(next_page_selector):
                                break
                        except Exception as e:
                            logger.error(f"Error navigating to the next page: {str(e)}")
                            break

                    return all_job_listings
                else:
                    response = requests.get(url)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    all_job_listings = []
                    job_id = 0
                    for job_element in soup.select(website_config['job_selector']):
                        job_id += 1
                        all_job_listings.append(self.scrape_job(job_element, website_config, job_id))
                    return all_job_listings
            except RequestException:
                logger.warning(f"RequestException encountered on attempt {attempt + 1} of {max_attempts}")
                time.sleep(2)  # Wait for 2 seconds before the next attempt


    def load_more(self, load_more_selector):
        try:
            load_more_button = self.driver.find_element(By.CSS_SELECTOR, load_more_selector)
            last_height = self.driver.execute_script("return document.body.scrollHeight")

            try:
                # Use JavaScript to click the button
                self.driver.execute_script("arguments[0].click();", load_more_button)
            except WebDriverException as e:
                # If an error occurs, print it out and return False
                print(f"An error occurred while trying to click the load more button: {e}")
                return False

            time.sleep(7)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if last_height == new_height:
                return False
            last_height = new_height

            return True
        except NoSuchElementException:
            return False
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return False

    def navigate_next_page(self, next_page_selector):
        try:     
            if next_page_selector is not None and isinstance(next_page_selector, str):
                next_page_element = self.driver.find_elements(By.CSS_SELECTOR, next_page_selector)
                if next_page_element:
                    try:
                        # Try clicking the element first
                        next_page_element[-1].click()
                        
                    except WebDriverException:
                        next_page_url = next_page_element[-1].get_attribute("href")

                        if not next_page_url:
                            return False
                        else:
                            self.driver.get(next_page_url)
                    time.sleep(7)
                    return True
            return False
        except Exception as e:
            logger.error(f"Error in navigating to the next page: {e}")
            return False


    def infinite_scroll_page(self):
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(7)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def get_soup(self, url, load_more_selector=None, infinite_scroll=False, next_page_selector=None):
        html = self.load_website(url, load_more_selector, infinite_scroll, next_page_selector)
        return BeautifulSoup(html, 'html.parser')

    def scrape_jobs(self, website_config, job_categories, job_types):
        JobListing.objects.update(to_be_deleted=True)
        
        load_more_selector = website_config.get('load_more_selector', None)
        infinite_scroll = website_config.get('infinite_scroll', False)
        next_page_selector = website_config.get('next_page_selector', None)

        # We are getting or creating the company outside the loop.
        company_name = website_config.get('company_name', "Not Disclosing")
        company, created = Company.objects.get_or_create(name=company_name)
        if created:
            # If the company is newly created
            company_logo = website_config.get('company_logo', None)
            company_desc = website_config.get('company_desc', None)
            company_career_url = website_config.get('company_career_url', None)
            compnany_job_base_url = website_config.get('compnany_job_base_url', None)
            company_tags = website_config.get('company_tags', [])  # This should be a list of tag names
            # Add tags to the company
            for tag_name in company_tags:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                company.tags.add(tag)
            company.logo = company_logo
            company.description = company_desc
            company.career_url = company_career_url
            company.job_base_url = compnany_job_base_url
            company.save()

        all_job_listings = []
        for job in website_config['job_urls']:
            try:
                category_id = job.get('category_id')
                type_id = job.get('type_id')

                category_name = job_categories.get(category_id, None)
                type_name = job_types.get(type_id, None)
                
                if category_name:
                    category, _ = Category.objects.get_or_create(name=category_name)
                else:
                    print(f"Category name for id {category_id} is not found. Skipping this job.")
                    continue

                if type_name:
                    job_type, _ = JobType.objects.get_or_create(name=type_name)
                else:
                    print(f"Job type name for id {type_id} is not found. Skipping this job.")
                    continue    

                JobListing.objects.filter(company=company, job_type=job_type, category=category).update(to_be_deleted=True)

                for url in job.get('url', []):
                    job_listings = self.load_website(url, load_more_selector, infinite_scroll, next_page_selector, website_config, job_type, category)
                    all_job_listings.extend(job_listings)
                
                JobListing.objects.filter(to_be_deleted=True, company=company, category=category, job_type=job_type).delete()
            except Exception as e:
                JobListing.objects.filter(company=company, category=category, job_type=job_type).update(to_be_deleted=False)
                print(f"An error occurred: {e}")

        return all_job_listings

    @staticmethod
    def scrape_job(job_element, website_config, job_id, job_type, category):
        def get_text(element, selector, next_sibling=False):
            if selector is None:
                logger.warning(f"Selector for element '{element}' is missing in the website configuration.")
                return None
            selected_element = element.select_one(selector)
            if selected_element:
                if next_sibling:
                    next_element = selected_element.nextSibling
                    return next_element.strip() if next_element else None
                else:
                    return selected_element.get_text(strip=True)

            return None

        def get_link(element, selector, link_in_job_selector):
            if link_in_job_selector:  # If the job link is in the job_selector
                return element['href'] if 'href' in element.attrs else None
            elif selector is None:  # If the job link is not in the job_selector
                logger.warning(f"Selector for element '{element}' is missing in the website configuration.")
                return None
            else:
                selected_element = element.select_one(selector)
                return selected_element['href'] if selected_element and 'href' in selected_element.attrs else None

        # Extract details
        company_name = website_config.get('company_name', "Not Disclosing")
        company = Company.objects.get(name=company_name)

        title = get_text(job_element, website_config.get('title_selector', None))
        
        location = get_text(job_element, website_config.get('location_selector', None), website_config.get('next_sibling', None))
        print("LO", location)
        if location is None or location.strip() == "":
            location = "United States"
        date_posted_str = get_text(job_element, website_config.get('date_selector', None))
        
        # Updated date_posted conversion
        date_posted = None
        if date_posted_str is not None:
            try:
                date_posted = convert_date_format(date_posted_str)
            except ValueError as ve:
                logger.warning(f"Failed to convert '{date_posted_str}' to a date. Error: {ve}")

        link = get_link(job_element, website_config.get('link_selector', None), website_config.get('link_in_job_selector', False))     

        # Create job data
        job_data = {
            'title': title,
            'link': link,
        }

        # Create a hash of the job data
        job_hash = create_hash(job_data)

        # Get or create a Job object
        job, created = JobListing.objects.get_or_create(
            hash=job_hash,
            defaults={
                'company': company,
                'title': title,
                'location': location,
                'date_posted': date_posted,
                'link': link,
                'to_be_deleted': False,  # Newly scraped jobs are not marked as "to be deleted"
                'job_type': job_type,
                'category': category
            }
        )

        if not created:
            logger.info(f"Job already exists: {link}")
            # If the job exists, unmark it as "to_be_deleted" and update the hash
            job.to_be_deleted = False
            job.save()

        return job_data