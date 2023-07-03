from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Case, When, Value, DateTimeField, IntegerField
from datetime import datetime, timezone, timedelta
from django.utils import timezone
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

from jobs.models import JobListing, Company
from jobs.serializers import JobSerializer, CompanySerializer, CompnayAllJobSerializer

from jobs.job_titles import job_titles


SYNONYMS = {
    "software developer": ["software developer","software engineer"],
    "software engineer": ["software developer"],
    "programmer": ["developer", "engineer", "coder", "dev"],
    'frontend developer': ['front-end']
}

@api_view(['GET'])
def job_title_autocomplete(request):
    # Get the 'term' sent by the client
    search_term = request.GET.get('term')

    # Ensure it's not None and is a valid string
    if not search_term:
        return Response([])

    # Match job titles from the predefined list
    matching_jobs = [title for title in job_titles if search_term.lower() in title.lower()][:10]  # Limit to 10 results

    return Response(matching_jobs)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 21
    page_size_query_param = 'page_size'
    max_page_size = 21

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
        queryset = JobListing.objects.all().order_by('title')
        
        days = self.request.query_params.get('days', None)
        search = self.request.query_params.get('search', None)
        location = self.request.query_params.get('location', None)
        job_type = self.request.query_params.get('job_type', None)
        job_category = self.request.query_params.get('category', None)

        # Apply the filtering if 'days' is not None
        if days is not None:
            cutoff_date = timezone.now() - timedelta(days=int(days))
            queryset = queryset.filter(
                Q(date_posted__isnull=False, date_posted__gte=cutoff_date) |
                Q(date_posted__isnull=True, discovered_at__gte=cutoff_date)
            ).annotate(
                ordering_date=Case(
                    When(date_posted__isnull=False, then='date_posted'),
                    When(date_posted__isnull=True, then='discovered_at'),
                    output_field=DateTimeField()
                ),
                priority=Case(
                    When(date_posted__isnull=False, then=Value(0)),
                    When(date_posted__isnull=True, then=Value(1)),
                    output_field=IntegerField()
                )
            ).order_by('priority', '-ordering_date')


        if search is not None and search != '':
            vector = SearchVector('title')
            # Look up any synonyms for the search term
            synonyms = SYNONYMS.get(search.lower(), [])
            # Create a SearchQuery for the search term and any synonyms
            query = SearchQuery(search, search_type='plain')
            for synonym in synonyms:
                query |= SearchQuery(synonym, search_type='plain')
            queryset = queryset.annotate(rank=SearchRank(vector, query)).filter(rank__gte=0.01).order_by('-rank')

        if location is not None:
            queryset = queryset.filter(location__icontains=location)
        
        

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
            cutoff_date = timezone.now() - timedelta(days=int(days))
            jobs = jobs.filter(
                Q(date_posted__isnull=False, date_posted__gte=cutoff_date) |
                Q(date_posted__isnull=True, discovered_at__gte=cutoff_date)
            ).annotate(
                ordering_date=Case(
                    When(date_posted__isnull=False, then='date_posted'),
                    When(date_posted__isnull=True, then='discovered_at'),
                    output_field=DateTimeField()
                ),
                priority=Case(
                    When(date_posted__isnull=False, then=Value(0)),
                    When(date_posted__isnull=True, then=Value(1)),
                    output_field=IntegerField()
                )
            ).order_by('priority', '-ordering_date')

        page = self.paginate_queryset(jobs)
        if page is not None:
            serializer = CompnayAllJobSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = CompnayAllJobSerializer(jobs, many=True)
        return Response(serializer.data)
