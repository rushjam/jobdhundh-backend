from django.db import models
from django.utils import timezone

class JobType(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name
    
class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name
    
class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name

class Company(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, null=True)
    logo = models.URLField(max_length=200, null=True) 
    description = models.TextField(null=True)
    career_url = models.URLField(max_length=200, null=True)
    job_base_url = models.URLField(max_length=200, null=True)
    tags = models.ManyToManyField(Tag, blank=True)

    def job_count(self):
        return JobListing.objects.filter(company=self).count()

    def jobs_posted_today(self):
        return JobListing.objects.filter(company=self, discovered_at__date=timezone.now().date()).count()

    def __str__(self):
        return self.name

class JobListing(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200, null=True)
    job_type = models.ForeignKey(JobType, on_delete=models.SET_NULL, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    location = models.CharField(max_length=200, null=True)
    date_posted = models.DateTimeField(blank=True, null=True)
    link = models.URLField(max_length=500, null=True)
    hash = models.CharField(max_length=32, unique=True, null=True)  # MD5 hash length is 32
    to_be_deleted = models.BooleanField(default=False)
    discovered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

