from django.urls import path
from rest_framework.routers import DefaultRouter
from .. import views
from rest_framework.authtoken.views import ObtainAuthToken


urlpatterns = [
    # profile
    path("", views.ProfileApiView.as_view(), name="profile"),
]
