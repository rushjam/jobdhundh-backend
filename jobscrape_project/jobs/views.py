from rest_framework import viewsets
from jobs.models import JobListing
from jobs.serializers import JobSerializer

class JobViewSet(viewsets.ModelViewSet):
    queryset = JobListing.objects.all()
    serializer_class = JobSerializer
