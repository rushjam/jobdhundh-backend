from rest_framework import serializers
from urllib.parse import urljoin
from django.utils.timezone import localtime
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
    date_posted = serializers.SerializerMethodField()
    discovered_at = serializers.SerializerMethodField()
    link = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    job_type = serializers.SerializerMethodField()
    
    def get_date_posted(self, obj):
        if obj.date_posted is None:
            return None
        return localtime(obj.date_posted).strftime('%b %d, %Y')
    def get_discovered_at(self, obj):
        return localtime(obj.discovered_at).strftime('%b %d, %Y')
    def get_link(self, obj):
        if obj.company.job_base_url:
            full_url = urljoin(obj.company.job_base_url, obj.link)
        else:
            full_url = obj.link
        return full_url
    def get_category(self, obj):
        return obj.category.name
    def get_job_type(self, obj):
        return obj.job_type.name
    
    class Meta:
        model = JobListing
        fields = ['id', 'job_type', 'category', 'title', 'location', 'date_posted', 'link', 'discovered_at', 'company']

    

class CompnayAllJobSerializer(serializers.ModelSerializer):
    date_posted = serializers.SerializerMethodField()
    discovered_at = serializers.SerializerMethodField()
    link = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    job_type = serializers.SerializerMethodField()

    def get_date_posted(self, obj):
        if obj.date_posted is None:
            return None
        return localtime(obj.date_posted).strftime('%b %d, %Y')
    def get_discovered_at(self, obj):
        return localtime(obj.discovered_at).strftime('%b %d, %Y')
    def get_link(self, obj):
        if obj.company.job_base_url:
            full_url = urljoin(obj.company.job_base_url, obj.link)
        else:
            full_url = obj.link
        return full_url
    def get_category(self, obj):
        return obj.category.name
    def get_job_type(self, obj):
        return obj.job_type.name

    class Meta:
        model = JobListing
        fields = ['id','job_type', 'category', 'title', 'location', 'date_posted', 'link', 'discovered_at']

    