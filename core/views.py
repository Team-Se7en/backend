from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.viewsets import GenericViewSet

from .serializers import *

# Create your views here.


class CutomObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainSerializer
