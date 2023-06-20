import json
from django.core.management.base import BaseCommand
import time

from utils.job_scraper import JobScraper

class Command(BaseCommand):
    help = "Command to start scraping jobs"

    def handle(self, *args, **kwargs):
        start_time = time.time()

        # Load the websites configuration
        with open('data/websites.json', 'r') as f:
            websites = json.load(f)

        # Initialize the scraper
        scraper = JobScraper(driver_path='drivers/chromedriver.exe', dynamic=True)

        # Scrape jobs
        all_job_listings = []
        for website in websites:
            job_listings = scraper.scrape_jobs(website)
            all_job_listings.extend(job_listings)

        for job in all_job_listings:
            self.stdout.write(self.style.SUCCESS(f"Scraped job: {job}"))
        
        time_difference = time.time() - start_time
        print(f'Scraping time: %.2f seconds.' % time_difference)
    
    
