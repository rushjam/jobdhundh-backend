from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from datetime import datetime, timezone, timedelta
from django.utils import timezone

from jobs.models import JobListing, Company
from jobs.serializers import JobSerializer, CompanySerializer, CompnayAllJobSerializer

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 21
    page_size_query_param = 'page_size'
    max_page_size = 1000

    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'results': data
        })
    
class JobViewSet(viewsets.ModelViewSet):
    queryset = JobListing.objects.all()
    serializer_class = JobSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = JobListing.objects.all().order_by('-discovered_at')
        
        # Print the count before filtering
        print("Count before filtering: ", queryset.count())
        
        days = self.request.query_params.get('days', None)
        if days is not None:
            # Filter jobs discovered within the last `days` days
            cutoff_date = timezone.now() - timedelta(days=int(days))
            
            # Print the days and cutoff_date
            print("Days from request: ", days)
            print("Cutoff date: ", cutoff_date)
            
            queryset = queryset.filter(discovered_at__gte=cutoff_date)
        
        # Print the count after filtering and the queryset itself
        print("Count after filtering: ", queryset.count())
        print(queryset)
        
        return queryset

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = Company.objects.all()
        
        tags = self.request.query_params.getlist('tag', None)
        if tags:
            for tag in tags:
                queryset = queryset.filter(tags__name__iexact=tag)

        return queryset
    
    @action(detail=True)
    def jobs(self, request, pk=None):
        jobs = JobListing.objects.filter(company_id=pk)

        days = self.request.query_params.get('days', None)
        if days is not None:
            # Filter jobs discovered within the last `days` days
            cutoff_date = timezone.now() - timedelta(days=int(days))
            jobs = jobs.filter(discovered_at__gte=cutoff_date)

        page = self.paginate_queryset(jobs)
        if page is not None:
            serializer = CompnayAllJobSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = CompnayAllJobSerializer(jobs, many=True)
        return Response(serializer.data)
