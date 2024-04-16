from django.urls import path,include
from . import views
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('students',views.StudentViewSet)

urlpatterns = router.urls