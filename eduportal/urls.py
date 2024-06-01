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
router.register(
    "stud_requests", views.StudentRequestListSearchViewSet, basename="stud_request"
)
router.register("admissions", views.AdmissionViewSet, basename="admission")
router.register("userinfo", views.UserInfoViewSet, basename="userinfo")
router.register("top_students", views.Top5StudentsViewSet, basename="top_students")
router.register(
    "top_professors", views.Top5ProfessorsViewSet, basename="top_professors"
)
router.register(
    "prof_own_position_filter",
    views.ProfessorOwnPositionFilteringViewSet,
    basename="prof_own_position_filter",
)
router.register(
    "prof_own_position_search",
    views.ProfessorOwnPositionSearchViewSet,
    basename="prof_own_position_search",
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
router.register("notifications", views.NotificationViewSet, basename="notification")
router.register("chat_list", views.ChatListViewSet, basename="chat_list")
router.register("messages", views.ChatMessagesViewSet, basename="chat_messages")
router.register(
    "message_last_seen_update",
    views.UpdateLastSeenMessageViewSet,
    basename="update_last_seen",
)
router.register("create_message", views.CreateMessageViewSet, basename="create_message")
router.register("delete_message", views.DeleteMessageViewSet)
router.register("edit_message", views.EditMessageViewSet, basename="edit_message")
router.register(
    "student_new_chat", views.NoChatProfessorsListViewset, basename="newChatProfessor"
)
router.register(
    "professor_new_chat", views.NoChatStudentsListViewset, basename="newChatStudent"
)
router.register("start_new_chat", views.StartNewChatViewSet, basename="start_new_chat")
router.register(
    "number_of_new_messages",
    views.NewMessagesCountViewSet,
    basename="new_message_count",
)


professors_router = routers.NestedSimpleRouter(router, "professors", lookup="professor")

professors_router.register(
    "CV/work-xps",
    views.WorkExperienceViewSet,
    basename="professor-CV-xps",
)
professors_router.register(
    "CV/education",
    views.EducationHistoryViewSet,
    basename="professor-education",
)
professors_router.register(
    "CV/projects",
    views.ProjectExperienceViewSet,
    basename="professor-projects",
)
professors_router.register(
    "CV/hard-skills",
    views.HardSkillViewSet,
    basename="professor-hard-skills",
)
professors_router.register(
    "CV/language-skills",
    views.LanguageSkillViewSet,
    basename="professor-language-skills",
)

students_router = routers.NestedSimpleRouter(router, "students", lookup="student")

students_router.register(
    "CV/work-xps",
    views.WorkExperienceViewSet,
    basename="student-CV-xps",
)
students_router.register(
    "CV/education",
    views.EducationHistoryViewSet,
    basename="student-education",
)
students_router.register(
    "CV/projects",
    views.ProjectExperienceViewSet,
    basename="student-projects",
)
students_router.register(
    "CV/hard-skills",
    views.HardSkillViewSet,
    basename="student-hard-skills",
)
students_router.register(
    "CV/language-skills",
    views.LanguageSkillViewSet,
    basename="student-language-skills",
)


urlpatterns = [
    path(
        "professors/<int:professor_pk>/CV/",
        views.CVAPIView.as_view(),
        name="professor-cv",
    ),
    path(
        "students/<int:student_pk>/CV/",
        views.CVAPIView.as_view(),
        name="student-cv",
    ),
    path("model_form_upload/", views.model_form_upload),
]
urlpatterns += router.urls
urlpatterns += professors_router.urls
urlpatterns += students_router.urls
