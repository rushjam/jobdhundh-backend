from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotAuthenticated, NotFound
from rest_framework_simplejwt.authentication import JWTAuthentication

from django.db.models import Q, Case, When, Value, DateTimeField, IntegerField
from django.utils import timezone
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.contrib.auth.models import User
from django.contrib.auth import login, get_user_model
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.http import JsonResponse

from jobs.models import JobListing, Company, UserProfile
from jobs.serializers import JobSerializer, CompanySerializer, CompnayAllJobSerializer, UserProfileSerializer

from .utils import create_jwt
from oauthlib.oauth2 import OAuth2Error as OAuthError
from authlib.integrations.django_client import OAuth
from urllib.parse import quote_plus, urlencode
from dotenv import load_dotenv
from datetime import timezone, timedelta
import json
import os


load_dotenv()
User = get_user_model()
oauth = OAuth()

oauth.register(
    "auth0",
    client_id=os.getenv('AUTH0_CLIENT_ID'),
    client_secret=os.getenv('AUTH0_CLIENT_SECRET'),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{os.getenv('AUTH0_DOMAIN')}/.well-known/openid-configuration",
)

SYNONYMS = {
    "software developer": ["software developer", "software engineer"],
    "software engineer": ["software developer"],
    "programmer": ["developer", "engineer", "coder", "dev"],
    'frontend developer': ['front-end']
}

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
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def save_job(self, request, pk=None):
        job = self.get_object()
        request.user.userprofile.saved_jobs.add(job)
        return Response({"status": "Job saved"}, status=200)

    @action(detail=True, methods=['post'])
    def unsave_job(self, request, pk=None):
        job = self.get_object()
        request.user.userprofile.saved_jobs.remove(job)
        return Response({"status": "Job removed"}, status=200)
    
    def get_queryset(self):
        queryset = JobListing.objects.all().order_by('title')

        days = self.request.query_params.get('days', None)
        search = self.request.query_params.get('search', None)
        location = self.request.query_params.get('location', None)
        category = self.request.query_params.get('category', None)
        job_types = self.request.query_params.getlist('job_type', None)

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
            queryset = queryset.annotate(rank=SearchRank(vector, query)).filter(
                rank__gte=0.01).order_by('-rank')

        if location is not None:
            queryset = queryset.filter(state_location__iexact=location)

        if category is not None:
            queryset = queryset.filter(category__name__iexact=category)

        if job_types:
            queryset = queryset.filter(job_type__name__in=job_types)

        return queryset

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    pagination_class = StandardResultsSetPagination
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Company.objects.all()

        tags = self.request.query_params.getlist('tag', None)
        if tags:
            for tag in tags:
                queryset = queryset.filter(tags__name__iexact=tag)

        return queryset

    @action(detail=True)
    def jobs(self, request, pk=None):
        jobs = JobListing.objects.filter(company_id=pk).order_by('title')

        days = self.request.query_params.get('days', None)
        search = self.request.query_params.get('search', None)
        location = self.request.query_params.get('location', None)
        category = self.request.query_params.get('category', None)
        job_types = self.request.query_params.getlist('job_type', None)

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
    
        if search is not None and search != '':
            vector = SearchVector('title')
            # Look up any synonyms for the search term
            synonyms = SYNONYMS.get(search.lower(), [])
            # Create a SearchQuery for the search term and any synonyms
            query = SearchQuery(search, search_type='plain')
            for synonym in synonyms:
                query |= SearchQuery(synonym, search_type='plain')
            jobs = jobs.annotate(rank=SearchRank(vector, query)).filter(
                rank__gte=0.01).order_by('-rank')

        if location is not None:
            jobs = jobs.filter(state_location__iexact=location)

        if category is not None:
            jobs = jobs.filter(category__name__iexact=category)

        if job_types:
            jobs = jobs.filter(job_type__name__in=job_types)

        page = self.paginate_queryset(jobs)
        if page is not None:
            serializer = CompnayAllJobSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = CompnayAllJobSerializer(jobs, many=True)
        return Response(serializer.data)

class UserProfileViewSet(viewsets.GenericViewSet,
                         RetrieveModelMixin,
                         UpdateModelMixin):
    """
    ViewSet for user profiles.
    """
    serializer_class = UserProfileSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Returns the queryset for user profiles of the currently authenticated user.
        """
        try:
            if not self.request.user.is_authenticated:
                raise NotAuthenticated("No user is logged in")
            return UserProfile.objects.filter(user=self.request.user)
        except UserProfile.DoesNotExist:
            raise NotFound("User profile not found")
    
    @action(detail=False, methods=['post'])
    def save_job(self, request):
        job_id = request.data.get('id')
        if not job_id:
            return Response({"detail": "Missing job_id"}, status=400)
        
        job = get_object_or_404(JobListing, id=job_id)
        request.user.userprofile.saved_jobs.add(job)
        return Response({"status": "Job saved"}, status=200)

    @action(detail=False, methods=['post'])
    def unsave_job(self, request):
        job_id = request.data.get('id')
        if not job_id:
            return Response({"detail": "Missing job_id"}, status=400)
        
        job = get_object_or_404(JobListing, id=job_id)
        request.user.userprofile.saved_jobs.remove(job)
        return Response({"status": "Job unsaved"}, status=200)

    @action(detail=False, methods=['post'])
    def save_company(self, request):
        company_id = request.data.get('id')
        if not company_id:
            return Response({"detail": "Missing company_id"}, status=400)
        
        company = get_object_or_404(Company, id=company_id)
        request.user.userprofile.saved_companies.add(company)
        return Response({"status": "Company saved"}, status=200)

    @action(detail=False, methods=['post'])
    def unsave_company(self, request):
        company_id = request.data.get('id')
        if not company_id:
            return Response({"detail": "Missing company_id"}, status=400)
        
        company = get_object_or_404(Company, id=company_id)
        request.user.userprofile.saved_companies.remove(company)
        return Response({"status": "Company unsaved"}, status=200)

    @action(detail=False, methods=['get', 'patch'])
    def me(self, request):
        """
        Handle requests to the /me endpoint.
        """
        try:
            if request.method == 'GET':
                serializer = self.get_serializer(self.request.user.userprofile)
            else:  # request.method == 'PATCH':
                serializer = self.get_serializer(
                    self.request.user.userprofile,
                    data=request.data,
                    partial=True  # for partial update
                )
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
            return Response(serializer.data)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)

def index(request):
    user_info = request.session.get("user")
    return render(
        request,
        "index.html",
        context={
            "session": user_info,
            "pretty": json.dumps(user_info, indent=4) if user_info else None,
        },
    )

def callback(request):
    """
    Callback function for the authentication process.
    """
    try:
        token = oauth.auth0.authorize_access_token(request)
        userinfo_endpoint = oauth.auth0.load_server_metadata()["userinfo_endpoint"]
        resp = oauth.auth0.get(userinfo_endpoint, token=token)
        user_info = resp.json()



        # Get the Django user associated with this Auth0 user
        # Or create a new one if this is a new user
        username = user_info["email"]  # Assuming the email is unique
        user, created = User.objects.get_or_create(username=username)

        # If the user was just created, you may want to set other user fields here
        # If the Auth0 user has fields like name or picture, you could set those on your Django user
        if created:
            user.email = username  # Set the email, for example
            user.save()

        # Use Django's built-in login function
        # It takes care of saving the user's ID in the session
        # It also sets request.user for the duration of this request
        login(request, user) 

        # Generate JWT token and store it in the session
        jwt_token = create_jwt(user)  # call to utility function defined in utils.py
        
        request.session['user'] = user_info


        return JsonResponse({"jwt_token": jwt_token, "user_info": user_info})
    except OAuthError as oe:  # You need to import OAuthError
        return Response({"detail": "OAuth failed: " + str(oe)}, status=400)
    except Exception as e:
        return Response({"detail": str(e)}, status=500)

def login_view(request):
    try:
        return oauth.auth0.authorize_redirect(
            request, request.build_absolute_uri(reverse("callback"))
        )
    except OAuthError as oe:
        return Response({"detail": "OAuth failed: " + str(oe)}, status=400)

def logout_view(request):
    try:
        request.session.clear()

        return redirect(
            f"https://{os.getenv('AUTH0_DOMAIN')}/v2/logout?"
            + urlencode(
                {
                    "returnTo": request.build_absolute_uri(reverse("/")),
                    "client_id": os.getenv('AUTH0_CLIENT_ID'),
                },
                quote_via=quote_plus,
            ),
        )
    except Exception as e:
        return Response({"detail": str(e)}, status=500)