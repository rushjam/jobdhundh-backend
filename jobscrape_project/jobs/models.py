from django.db import models
from django.utils import timezone

class Company(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, null=True)
    logo = models.ImageField(upload_to='company_logos/', null=True, blank=True)  # if you want to add logos to companies
    description = models.TextField(null=True)

    def job_count(self):
        return JobListing.objects.filter(company=self).count()

    def jobs_posted_today(self):
        return JobListing.objects.filter(company=self, date_posted__date=timezone.now().date()).count()
    
    # when you convert a Company object to JSON, these fields can be accessed as:
    # company.job_count and company.jobs_posted_today

    def __str__(self):
        return self.name

class JobListing(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    location = models.CharField(max_length=200, null=True)
    description = models.TextField(null=True)
    date_posted = models.DateTimeField(blank=True, null=True)
    link = models.URLField(max_length=500, null=True)
    hash = models.CharField(max_length=32, unique=True, null=True)  # MD5 hash length is 32
    to_be_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.title

# class CompanyJobCount(models.Model):
#     company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='job_counts')
#     total_jobs = models.IntegerField(default=0)
#     today_posted_jobs = models.IntegerField(default=0)

#     def __str__(self):
#         return f'Job count for {self.company.name}'

