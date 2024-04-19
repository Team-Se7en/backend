from django.urls import path
from django.urls.conf import include
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register("professors", views.ProfessorViewSet)
router.register("positions", views.PositionViewSet, basename="positions")

urlpatterns = []
urlpatterns += router.urls
