from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q

from jobs.models import JobListing

class Command(BaseCommand):
    help = 'Delete all jobs that are more than a month old'

    def handle(self, *args, **options):
        # Calculate the date a month ago from now
        one_month_ago = timezone.now() - timedelta(days=45)

        # Get all jobs older than a month, considering both date_posted and discovered_at
        old_jobs = JobListing.objects.filter(
            Q(date_posted__lt=one_month_ago) | 
            Q(discovered_at__lt=one_month_ago, date_posted__isnull=True)
        )

        # Delete these jobs
        old_jobs.delete()

        self.stdout.write(self.style.SUCCESS('Successfully deleted old jobs'))
