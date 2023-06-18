from rest_framework import viewsets
from jobs.models import JobListing
from jobs.models import Company
from jobs.serializers import JobSerializer
from jobs.serializers import CompanySerializer

class JobViewSet(viewsets.ModelViewSet):
    queryset = JobListing.objects.all()
    serializer_class = JobSerializer

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer