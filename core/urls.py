from django.urls import path, include
from rest_framework_nested import routers
from rest_framework.routers import SimpleRouter

from . import views

urlpatterns = [
    path("", include("djoser.urls")),
    path("", include("djoser.urls.jwt")),
]