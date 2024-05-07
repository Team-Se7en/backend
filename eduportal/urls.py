from django.urls import path, include
from django.urls.conf import include
from rest_framework_nested import routers
from rest_framework.routers import SimpleRouter

from . import views

router = routers.DefaultRouter()
router.register("universities", views.UniversityViewSet, basename="universities")
router.register("students", views.StudentGetListViewSet)
router.register("student-profile", views.StudentProfileViewSet, "student_profile")
router.register("professors", views.ProfessorViewSet)
router.register("positions", views.PositionViewSet, basename="positions")
router.register("tags", views.TagListViewSet)
router.register("requests", views.RequestViewSet, basename="request")
router.register("admissions", views.AdmissionViewSet, basename="admission")
router.register("userinfo", views.UserInfoViewSet, basename="userinfo")
router.register(
    "prof_own_position_filter",
    views.ProfessorOwnPositionFilteringViewSet,
    basename="prof_own_position_filter",
)
router.register(
    "prof_other_position_filter",
    views.ProfessorOtherPositionFilteringViewSet,
    basename="prof_other_position_filter",
)
router.register(
    "stud_position_filter",
    views.StudentPositionFilteringViewSet,
    basename="stud_pos_fil",
)
router.register(
    "stud_req_filter",
    views.StudentRequestFilteringViewSet,
    basename="stud_req_filtering",
)
router.register(
    "prof_req_filter",
    views.ProfessorRequestFilteringViewSet,
    basename="prof_req_filtering",
)

router.register("landing", views.LandingViewSet, basename="landing")


professors_router = routers.NestedSimpleRouter(router, "professors", lookup="professor")

professors_router.register(
    "CV/work-xps",
    views.ProfessorWorkExperienceViewSet,
    basename="professor-CV-xps",
)
professors_router.register(
    "CV/education",
    views.ProfessorEducationHistoryViewSet,
    basename="professor-education",
)
professors_router.register(
    "CV/projects",
    views.ProfessorProjectExperienceViewSet,
    basename="professor-projects",
)
professors_router.register(
    "CV/hard-skills",
    views.ProfessorHardSkillViewSet,
    basename="professor-hard-skills",
)


urlpatterns = [
    path(
        "professors/<int:professor_pk>/CV/",
        views.ProfessorCVAPIView.as_view(),
        name="professor-cv",
    ),
]
urlpatterns += router.urls
urlpatterns += professors_router.urls
