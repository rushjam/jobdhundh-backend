from rest_framework import serializers
from .models import JobListing, Company, Tag

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class CompanySerializer(serializers.ModelSerializer):
    job_count = serializers.IntegerField(read_only=True)
    jobs_posted_today = serializers.IntegerField(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Company
        fields = '__all__' # This means all fields of the Job model will be included. Adjust this if needed.

class JobCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'logo']

class JobSerializer(serializers.ModelSerializer):
    company = JobCompanySerializer(read_only=True)

    class Meta:
        model = JobListing
        fields = ['id', 'company', 'title', 'location', 'date_posted', 'link', 'discovered_at']

class CompnayAllJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobListing
        fields = ['id', 'title', 'location', 'date_posted', 'link', 'discovered_at']