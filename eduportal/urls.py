from django.urls import path,include
from . import views
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('students',views.StudentGetListViewSet)
router.register('student-profile',views.StudentProfileViewSet,'student_profile')

urlpatterns = [
    path('',include(router.urls)),
]
