import time
import requests
import logging
import hashlib
import json

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from selenium.common.exceptions import NoSuchElementException
from requests.exceptions import RequestException

from jobs.models import JobListing
from jobs.models import Company

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
        self.driver = webdriver.Chrome(options=chrome_options)

    def __del__(self):
        self.driver.quit()

    def load_website(self, url, load_more_selector=None, infinite_scroll=False, next_page_selector=None, website_config=None):
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
                            all_job_listings.append(self.scrape_job(job_element, website_config, job_id))
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
                break
            except RequestException:
                logger.warning(f"RequestException encountered on attempt {attempt + 1} of {max_attempts}")
                time.sleep(2)  # Wait for 2 seconds before the next attempt


    def load_more(self, load_more_selector):
        try:
            load_more_button = self.driver.find_element(By.CSS_SELECTOR, load_more_selector)
            if load_more_button.text == 'Load more':
                load_more_button.click()
                time.sleep(7)
                return True
            else:
                return False
        except NoSuchElementException:
            return False

    def navigate_next_page(self, next_page_selector):
        try:
            if next_page_selector is not None and isinstance(next_page_selector, str):
                next_button = self.driver.find_elements(By.CSS_SELECTOR, next_page_selector)
                if next_button:
                    next_button[-1].click()
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

    def scrape_jobs(self, website_config):
        # Get the company name
        company_name = website_config.get('company_name', "Not Disclosing")

        # Try to get the company by name, create it if it does not exist
        company, created = Company.objects.get_or_create(name=company_name)

        # Mark only this company's jobs as "to be deleted"
        JobListing.objects.filter(company=company).update(to_be_deleted=True)

        url = website_config['url']
        load_more_selector = website_config.get('load_more_selector', None)
        infinite_scroll = website_config.get('infinite_scroll', False)
        next_page_selector = website_config.get('next_page_selector', None)

        all_job_listings = self.load_website(url, load_more_selector, infinite_scroll, next_page_selector, website_config)
        
        # Delete only this company's jobs that are still marked as "to_be_deleted"
        JobListing.objects.filter(to_be_deleted=True, company=company).delete()
        

        return all_job_listings

    @staticmethod
    def scrape_job(job_element, website_config, job_id):
        def get_text(element, selector):
            if selector is None:
                logger.warning(f"Selector for element '{element}' is missing in the website configuration.")
                return None
            selected_element = element.select_one(selector)
            return selected_element.get_text(strip=True) if selected_element else None

        def get_link(element, selector):
            if selector is None:
                logger.warning(f"Selector for element '{element}' is missing in the website configuration.")
                return None
            selected_element = element.select_one(selector)
            return selected_element['href'] if selected_element and 'href' in selected_element.attrs else None

        # Extract details
        company_name = website_config.get('company_name', "Not Disclosing")
        # Try to get the company by name, create it if it does not exist
        company, created = Company.objects.get_or_create(name=company_name)

        title = get_text(job_element, website_config.get('title_selector', None))
        location = get_text(job_element, website_config.get('location_selector', None))
        date_posted = None
        description = get_text(job_element, website_config.get('description_selector', None))
        link = get_link(job_element, website_config.get('link_selector', None))
        

        # Create job data
        job_data = {
            'id': job_id,
            'title': title,
            'location': location,
            'date_posted': date_posted,
            'description': description,
            'link': link,
        }

        # Create a hash of the job data
        job_hash = create_hash(job_data)
       
        # Check if a job with the same hash already exists in the database
        job_exists = JobListing.objects.filter(hash=job_hash)

        if not job_exists.exists():
            # Create a new Job object and save it into the database
            job = JobListing(
                company=company,
                title=title,
                location=location,
                date_posted=date_posted,
                description=description,
                link=link,
                hash=job_hash,  # Save the hash
                to_be_deleted=False,  # Newly scraped jobs are not marked as "to be deleted"
            )
            job.save()
        else:
            logger.info(f"Job already exists: {link}")
            # If the job exists, unmark it as "to_be_deleted" and update the hash
            job = job_exists.first()  # Fetch the existing job
            job.to_be_deleted = False
            job.hash = job_hash  # Update the hash
            job.save()

        return job_data

