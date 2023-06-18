from rest_framework import viewsets
from jobs.models import JobListing
from jobs.serializers import JobSerializer

class JobViewSet(viewsets.ModelViewSet):
    queryset = JobListing.objects.all()
    for job in queryset:
        print("=-=-=-=", job)
    serializer_class = JobSerializer
