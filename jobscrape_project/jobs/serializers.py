from rest_framework import serializers
from .models import JobListing

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobListing
        fields = '__all__' # This means all fields of the Job model will be included. Adjust this if needed.
