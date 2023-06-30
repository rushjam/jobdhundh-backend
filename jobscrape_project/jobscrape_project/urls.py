from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from jobs import views
from jobs.views import job_title_autocomplete

router = routers.DefaultRouter()
router.register(r'jobs', views.JobViewSet, basename='job')
router.register(r'companies', views.CompanyViewSet, basename='company')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('job_title_autocomplete/', job_title_autocomplete, name='job_title_autocomplete'),
]
