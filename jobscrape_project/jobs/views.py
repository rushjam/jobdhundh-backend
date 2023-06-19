from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination


from jobs.models import JobListing, Company
from jobs.serializers import JobSerializer, CompanySerializer

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

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    pagination_class = StandardResultsSetPagination

    @action(detail=True)
    def jobs(self, request, pk=None):
        jobs = JobListing.objects.filter(company_id=pk)

        page = self.paginate_queryset(jobs)
        if page is not None:
            serializer = JobSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data)
