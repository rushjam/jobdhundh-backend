from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q

from jobs.models import JobListing, Company

class Command(BaseCommand):
    help = 'Delete all jobs that are more than a month old'

    def handle(self, *args, **options):
        # Calculate the date a month ago from now
        one_month_ago = timezone.now() - timedelta(days=30)

        # Get all jobs older than a month, considering both date_posted and discovered_at
        old_jobs = JobListing.objects.filter(
            Q(date_posted__lt=one_month_ago) | 
            Q(discovered_at__lt=one_month_ago, date_posted__isnull=True)
        )

        # Delete these jobs
        old_jobs.delete()

        self.stdout.write(self.style.SUCCESS('Successfully deleted old jobs'))
        # company_id = 7
        # try:
        #     company = Company.objects.get(id=company_id)  # get the Company instance with the provided id
        #     company.delete()  # this will also delete all associated JobListing instances due to the CASCADE relation
        #     print(f"Company and its associated job listings with id {company_id} have been deleted.")
        # except Company.DoesNotExist:
        #     print(f"No company found with id {company_id}.")

