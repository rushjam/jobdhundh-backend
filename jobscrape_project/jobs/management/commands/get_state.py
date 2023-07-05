from django.core.management.base import BaseCommand
from jobs.models import JobListing
import requests
import os

from dotenv import load_dotenv

load_dotenv()

def get_location_info(location, API_KEY):
    response = requests.get(f'https://maps.googleapis.com/maps/api/geocode/json?address={location}&types=administrative_area_level_2&key={API_KEY}')
    data = response.json()
    administrative_area_level_1 = None

    if data['results']:
        for component in data['results'][0]['address_components']:
            if 'administrative_area_level_1' in component['types']:
                administrative_area_level_1 = component['long_name']
                break
    return administrative_area_level_1

class Command(BaseCommand):
    help = 'Get State name by giving the city name'

    def handle(self, *args, **options):
        API_KEY = os.getenv('GOOGLE_GEO_LOCATION_API')
        job_listings = JobListing.objects.exclude(location__iexact='United States').exclude(state_location__isnull=False)
        count = 0
        if job_listings:
            for job in job_listings:
                try:
                    location_info = get_location_info(job.location, API_KEY)
                    if location_info == None:
                        job.state_location = 'United States'
                    else:
                        job.state_location = location_info
                    job.save()
                    count +=1
                except (IndexError, KeyError):
                    self.stdout.write(self.style.ERROR(f'State name extraction failed for job id: {job.id}'))
        print(f"All the location's States are Added", count)
            
        

    
        
        

        

    
        
