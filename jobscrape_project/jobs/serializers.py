from rest_framework import serializers
from .models import JobListing
from .models import Company

class CompanySerializer(serializers.ModelSerializer):
    job_count = serializers.IntegerField(read_only=True)
    jobs_posted_today = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Company
        fields = '__all__' # This means all fields of the Job model will be included. Adjust this if needed.

class JobSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)

    class Meta:
        model = JobListing
        fields = '__all__' # This means all fields of the Job model will be included. Adjust this if needed.

