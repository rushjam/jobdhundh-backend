from django.db import models
from django.utils import timezone

# class JobListing(models.Model):
#     id = models.AutoField(primary_key=True)
#     title = models.CharField(max_length=200, null=True)
#     company = models.CharField(max_length=200, null=True)
#     location = models.CharField(max_length=200, null=True)
#     description = models.TextField(null=True)
#     date_posted = models.DateTimeField(blank=True, null=True)
#     link = models.URLField(max_length=500, null=True)
#     hash = models.CharField(max_length=32, unique=True, null=True)  # MD5 hash length is 32
#     to_be_deleted = models.BooleanField(default=False)

#     def __str__(self):
#         return self.title

class Company(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, null=True)
    logo = models.ImageField(upload_to='company_logos/', null=True, blank=True)  # if you want to add logos to companies
    description = models.TextField(null=True)

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
