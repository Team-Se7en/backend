from django.urls import path,include
from django.urls.conf import include
from rest_framework_nested import routers
from . import views
from rest_framework.routers import SimpleRouter

router = routers.DefaultRouter()
router.register('students',views.StudentGetListViewSet)
router.register('student-profile',views.StudentProfileViewSet,'student_profile')
router.register("professors", views.ProfessorViewSet)
router.register("positions", views.PositionViewSet, basename="positions")

urlpatterns = []
urlpatterns += router.urls
