from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from jobs import views

router = routers.DefaultRouter()
router.register(r'jobs', views.JobViewSet, basename='job')
router.register(r'companies', views.CompanyViewSet, basename='company')
router.register(r'userprofiles', views.UserProfileViewSet, basename='userprofile')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('userprofiles/me/', views.UserProfileViewSet.as_view({'get': 'me', 'patch': 'me'}), name='my-profile'),
    path('userprofiles/save_job', views.UserProfileViewSet.as_view({'post': 'save_job'}), name='save-job'),
    path('userprofiles/unsave_job', views.UserProfileViewSet.as_view({'post': 'unsave_job'}), name='unsave-job'),
    path('userprofiles/save_company', views.UserProfileViewSet.as_view({'post': 'save_company'}), name='save-company'),
    path('userprofiles/unsave_company', views.UserProfileViewSet.as_view({'post': 'unsave_company'}), name='unsave-company'),
    path('index/', views.index, name='index'),
    path("login", views.login_view, name="login_view"),
    path("logout", views.logout_view, name="logout_view"),
    path("callback", views.callback, name="callback")

]
