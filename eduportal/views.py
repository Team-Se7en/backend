from pprint import pprint
from random import sample
from django.contrib.auth import get_user_model
from django.db.models import Prefetch, Min, Count, Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.http import Http404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.mixins import *
from rest_framework.permissions import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from .models import *
from .permissions import *
from .serializers import *
from .utils.views import *
from .filters import *

User = get_user_model()

# Landing Views ----------------------------------------------------------------


class LandingViewSet(GenericViewSet):
    def list(self, request):
        professor_count = Professor.objects.count()
        student_count = Student.objects.count()
        return Response(
            {
                "professor_count": professor_count,
                "student_count": student_count,
                "growth": self.growth(request),
                "top_universities": self.top_universities(request),
                "top_professors": self.top_professors(request),
                "top_students": self.top_students(request),
                "professor_view_positions": self.random_top_positions(
                    request, ProfessorPositionListSerializer
                ),
                "student_view_positions": self.random_top_positions(
                    request, StudentPositionListSerializer
                ),
            }
        )

    def growth(self, request):
        qs = User.objects.only("date_joined")

        site_creation_date = qs.aggregate(Min("date_joined"))["date_joined__min"]

        today = timezone.now()

        delta = (today - site_creation_date) / 4
        date_points = [site_creation_date + i * delta for i in range(1, 5)]

        growth = []
        for date in date_points:
            user_count = qs.filter(date_joined__lte=date).count()
            growth.append((date.date(), user_count))

        return growth

    def top_universities(self, request):
        top_universities = University.objects.order_by("rank")[:8]
        serializer = LandingUniversitySerializer(top_universities, many=True)

        return serializer.data

    def top_professors(self, request):
        top_professors = self.get_top_professors()
        serializer = LandingProfessorSerializer(top_professors, many=True)

        return serializer.data

    def top_students(self, request):
        students = Student.objects.annotate(
            accepted_request_count=models.Count(
                "request", filter=models.Q(request__status="A")
            )
        )

        top_students = students.order_by("-accepted_request_count")[:3]
        serializer = LandingStudentSerializer(top_students, many=True)

        return serializer.data

    def random_top_positions(self, request, ser):
        positions = self.get_random_top_positions()
        serializer = ser(positions, many=True)

        return serializer.data

    def get_top_professors(self):
        professors = Professor.objects.annotate(
            accepted_request_count=models.Count(
                "positions__request", filter=models.Q(positions__request__status="A")
            )
        )

        return professors.order_by("-accepted_request_count")[:3]

    def get_random_top_positions(self):
        professors = self.get_top_professors()
        positions = (
            professors[0].positions.all() if professors else Position.objects.none()
        )
        for p in professors[1:]:
            positions = positions.union(p.positions.all())

        positions = list(positions)

        if len(positions) >= 2:
            random_positions = sample(positions, 2)
        else:
            random_positions = positions

        return random_positions


# User Views -------------------------------------------------------------------


class UserInfoViewSet(GenericViewSet):
    def list(self, request):
        user = request.user
        serializer = UserDetailSerializer(user, context={"request": self.request})
        return Response(serializer.data)


# University Views -------------------------------------------------------------


class UniversityViewSet(viewsets.ModelViewSet):
    serializer_class = UniversitySerializer

    def get_queryset(self):
        return University.objects.annotate(
            position_count=Count("professors__positions")
        )

    def get_permissions(self):
        match self.action:
            case "list" | "create" | "partial_update" | "update" | "destroy":
                return [IsAdminUser()]
            case "retrieve":
                return [AllowAny()]
            case _:
                return [AllowAny()]


# Student Views ----------------------------------------------------------------


class StudentGetListViewSet(
    ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Student.objects.select_related("user").all()
    serializer_class = StudentGetListSerializer
    filter_backends = [SearchFilter]
    search_fields = ["user__first_name", "user__last_name", "university__name"]


class StudentProfileViewSet(
    viewsets.GenericViewSet,
):
    queryset = Student.objects.all()
    serializer_class = OwnStudentProfileSerializer
    http_method_names = [
        "get",
        "patch",
        "delete",
    ]

    @action(
        detail=False,
        methods=["GET", "PATCH", "DELETE"],
        permission_classes=[IsAuthenticated],
    )
    def me(self, request, *args, **kwargs):
        student = get_object_or_404(Student, user_id=request.user.id)
        if request.method == "GET":
            serializer = OwnStudentProfileSerializer(student)
            return Response(serializer.data)
        elif request.method == "PATCH":
            serializer = OwnStudentProfileSerializer(
                student, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        elif request.method == "DELETE":
            user = student.user
            student.delete()
            user.delete()
            return Response(status=status.HTTP_202_ACCEPTED)


# Professor Views --------------------------------------------------------------


class ProfessorViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    GenericViewSet,
):
    http_method_names = ["get", "patch"]
    queryset = Professor.objects.select_related("user").all()
    serializer_class = ProfessorSerializer
    filter_backends = [SearchFilter]
    search_fields = ["user__first_name", "user__last_name"]

    @action(
        detail=False,
        methods=["GET", "PATCH"],
        permission_classes=[IsProfessor],
    )
    def me(self, request):
        professor = get_object_or_404(Professor, user_id=request.user.id)
        if request.method == "GET":
            serializer = ProfessorSerializer(professor)
            return Response(serializer.data)
        elif request.method == "PATCH":
            serializer = ProfessorSerializer(professor, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    @action(detail=False, methods=["GET"], permission_classes=[IsProfessor])
    def my_positions(self, request):
        professor = get_object_or_404(Professor, user_id=request.user.id)
        positions = Position.objects.filter(professor=professor)
        positions = positions.select_related(
            "professor", "professor__user"
        ).prefetch_related("tags", "tags2")
        serializer = OwnerPositionListSerializer(positions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["GET"], permission_classes=[IsProfessor])
    def my_recent_positions(self, request):
        professor = get_object_or_404(Professor, user_id=request.user.id)
        positions = Position.objects.filter(professor=professor).order_by(
            "-start_date"
        )[:5]
        positions = positions.select_related(
            "professor", "professor__user"
        ).prefetch_related("tags", "tags2")
        serializer = OwnerPositionListSerializer(positions, many=True)
        return Response(serializer.data)


# Position Views ---------------------------------------------------------------


class TagListViewSet(
    ListModelMixin,
    GenericViewSet,
):
    queryset = Tag.objects.all()
    serializer_class = ReadTagSerializer


class PositionViewSet(ModelViewSet):
    filter_backends = [SearchFilter]
    search_fields = [
        "title",
        "description",
        "professor__user__first_name",
        "professor__user__last_name",
        "professor__department",
        "professor__university__name",
        "tags__label",
    ]

    def get_serializer_class(self):
        action = self.action
        user = self.request.user
        user_type = get_user_type(self.request)
        match action:
            case "list":
                match user_type:
                    case "Anonymous":
                        return AnonymousPositionListSerializer
                    case "Student":
                        return StudentPositionListSerializer
                    case "Professor":
                        return ProfessorPositionListSerializer
                return None
            case "retrieve":
                match user_type:
                    case "Anonymous":
                        return AnonymousPositionDetailSerializer
                    case "Student":
                        return StudentPositionDetailSerializer
                    case "Professor":
                        if self.get_object().professor.user == user:
                            return OwnerPositionDetailSerializer
                        return ProfessorPositionDetailSerializer
                return None
            case "create" | "update" | "partial_update":
                return PositionUpdateSerializer
            case _:
                return None

    def get_queryset(self):
        user = self.request.user
        user_type = get_user_type(self.request)

        queryset = Position.objects.select_related(
            "professor", "professor__user"
        ).prefetch_related("tags", "tags2")

        if self.action == "list":
            queryset = queryset.exclude(professor__user__id=user.id)
        if self.action == "retrieve":
            if user_type == "Professor":
                requests_for_position = Request.objects.filter(
                    position__professor__user=user
                )
                queryset = queryset.prefetch_related(
                    Prefetch(
                        "request_set",
                        queryset=requests_for_position,
                        to_attr="position_requests",
                    )
                )

        if user_type == "Student":
            # Prefetch the Request objects for the current user
            requests_for_user = Request.objects.filter(student__user=user)
            queryset = queryset.prefetch_related(
                Prefetch(
                    "request_set",
                    queryset=requests_for_user,
                    to_attr="my_request",
                )
            )

        queryset = queryset.all()

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()

        user = self.request.user
        user_type = get_user_type(self.request)

        if user_type == "Student":
            context["student_id"] = user.student.id

        return context

    def get_permissions(self):
        if self.action == "list":
            return [AllowAny()]
        if self.action == "retrieve":
            return [AllowAny()]
        if self.action == "create":
            return [IsProfessor()]
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsProfessor(), IsPositionOwner()]
        else:
            return [AllowNone()]

    def create(self, request, *args, **kwargs):
        serializer = PositionUpdateSerializer(
            data=request.data, context={"professor_id": self.request.user.professor.id}
        )
        serializer.is_valid(raise_exception=True)
        position = serializer.save()
        serializer = ProfessorPositionDetailSerializer(position)
        return Response(serializer.data)


# Request Views ----------------------------------------------------------------


class StudentRequestListSearchViewSet(ModelViewSet):
    http_method_names = ["get"]
    queryset = Request.objects.all()
    serializer_class = StudentRequestListSeralizer
    permission_classes = [IsAuthenticated, IsProfessor]
    filter_backends = [SearchFilter]
    search_fields = ["student__user__first_name", "student__user__last_name"]

    def filter_queryset(self, queryset):
        if self.request.user.is_student:
            queryset = queryset.filter(student__id=self.request.user.student.id)
        else:
            queryset = queryset.select_related("position").filter(
                position__professor__id=self.request.user.professor.id
            )
        return super().filter_queryset(queryset)


class RequestViewSet(ModelViewSet):
    http_method_names = ["post", "get", "delete"]

    def get_queryset(self):
        return Request.objects.all()

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), IsStudent()]
        if self.action == "list":
            return [IsAuthenticated()]
        if self.action == "destroy":
            return [AllowNone()]
        if self.action == "retrieve":
            return [IsAuthenticated(), IsRequestOwner()]
        if self.action.startswith("professor"):
            return [IsAuthenticated(), IsProfessor(), IsRequestOwner()]
        if self.action.startswith("student"):
            return [IsAuthenticated(), IsStudent(), IsRequestOwner()]
        return [AllowNone()]

    def get_serializer_class(self):
        if self.action == "create":
            return StudentCreateRequestSerializer
        if self.action == "retrieve":
            if self.request.user.is_student:
                return StudentRequestDetailSerializer
            else:
                return ProfessorRequestDetailSerializer
        if self.action == "list":
            return RequestListSeralizer
        return RequestListSeralizer

    @action(
        detail=True,
        methods=["GET"],
        permission_classes=[IsAuthenticated, IsProfessor, IsRequestOwner],
    )
    def professor_accept_request(self, request, *args, **kwargs):
        request_id = int(kwargs["pk"])
        request_object = get_object_or_404(Request, pk=request_id)
        if request_object.status != "PP":
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        position = Position.objects.get(pk=request_object.position.id)
        if position.filled == position.capacity:
            return Response(
                "This position is filled.", status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        position.filled += 1
        position.save()
        request_object.status = "PA"
        request_object.save()
        return Response(status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["GET"],
        permission_classes=[IsAuthenticated, IsProfessor, IsRequestOwner],
    )
    def professor_reject_request(self, request, *args, **kwargs):
        request_id = int(kwargs["pk"])
        request_object = get_object_or_404(Request, pk=request_id)
        if request_object.status != "PP":
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        request_object.status = "PR"
        request_object.save()
        return Response(status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["GET"],
        permission_classes=[IsAuthenticated, IsStudent, IsRequestOwner],
    )
    def student_reject_request(self, request, *args, **kwargs):
        request_id = int(kwargs["pk"])
        request_object = get_object_or_404(Request, pk=request_id)
        if request_object.status != "PA":
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        position = Position.objects.get(pk=request_object.position.id)
        position.filled -= 1
        position.save()
        request_object.status = "SR"
        request_object.save()
        return Response(status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["GET"],
        permission_classes=[IsAuthenticated, IsStudent, IsRequestOwner],
    )
    def student_accept_request(self, request, *args, **kwargs):
        request_id = int(kwargs["pk"])
        request_object = get_object_or_404(Request, pk=request_id)
        if request_object.status != "PA":
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        request_object.status = "SA"
        request_object.save()
        return Response(status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        request_object = get_object_or_404(Request, pk=int(kwargs["pk"]))
        if request_object.student.user.id == request.user.id:
            return super().destroy(request, *args, **kwargs)
        else:
            return Response("Access denied", status=status.HTTP_403_FORBIDDEN)

    def list(self, request, *args, **kwargs):
        queryset = Request.objects
        if request.user.is_student:
            queryset = queryset.filter(student__id=request.user.student.id)
        else:
            queryset = queryset.select_related("position").filter(
                position__professor__id=request.user.professor.id
            )
        seializer = RequestListSeralizer(queryset, many=True)
        return Response(seializer.data)

    def create(self, request, *args, **kwargs):
        student = Student.objects.get(pk=request.user.student.id)
        sent_requests = student.request_set.filter(
            position__id=request.data.get("position_id")
        )
        if sent_requests.exists():
            if sent_requests.filter(status="R").exists():
                return Response(
                    "You are not allowed to request anymore",
                    status=status.HTTP_403_FORBIDDEN,
                )
            return Response(
                "Request already exists", status=status.HTTP_400_BAD_REQUEST
            )
        position = Position.objects.get(pk=request.data.get("position_id"))
        if position.filled == 1:
            Response(
                "This position is completed.", status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        if position.end_date < timezone.now().date():
            return Response(
                "The deadline is finished.", status=status.HTTP_405_METHOD_NOT_ALLOWED
            )

        serializer = StudentCreateRequestSerializer(
            data=request.data,
            context={
                "student_id": student.id,
            },
        )
        serializer.is_valid(raise_exception=True)
        saved_request = serializer.save()
        position.request_count += 1
        serializer = StudentCreateRequestSerializer(saved_request)
        return Response(serializer.data)


class AdmissionViewSet(UpdateModelMixin, ListModelMixin, GenericViewSet):
    http_method_names = ["get", "patch"]

    def get_queryset(self):
        if self.action == "list":
            return Request.objects.filter(status="A", share_with_others=True).all()
        if self.action == "partial_update":
            return Request.objects.filter(status="A").all()
        return None

    def get_permissions(self):
        if self.action == "list":
            return []
        if self.action == "partial_update":
            return [IsAuthenticated(), IsStudent(), IsRequestOwner()]
        return [AllowAny()]

    def get_serializer_class(self):
        if self.action == "list":
            return AdmissionSerializer
        elif self.action == "partial_update":
            return StudentRequestUpdateSeralizer

    def update(self, request, *args, **kwargs):
        request_object = get_object_or_404(Request, pk=int(kwargs["pk"]))
        if request_object.status != "A":
            return Response("Invalid admission.", status=status.HTTP_400_BAD_REQUEST)
        request_object.share_with_others = True
        return super().update(request, *args, **kwargs)


# Position Filtering Views -----------------------------------------------------


class ProfessorOwnPositionFilteringViewSet(ListModelMixin, GenericViewSet):
    serializer_class = ProfessorPositionFilterSerializer
    permission_classes = [IsAuthenticated, IsProfessor, IsPositionOwner]
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    filterset_class = ProfessorOwnPositionFilter
    ordering_fields = ["request_count", "fee", "position_start_date"]
    queryset = Position.objects.all()

    def filter_queryset(self, queryset):
        return (
            super()
            .filter_queryset(queryset)
            .filter(professor__id=self.request.user.professor.id)
        )


class ProfessorOwnPositionSearchViewSet(ListModelMixin, GenericViewSet):
    serializer_class = ProfessorPositionListSerializer
    permission_classes = [IsAuthenticated, IsProfessor, IsPositionOwner]
    filter_backends = [SearchFilter]
    filterset_class = ProfessorOwnPositionFilter
    search_fields = ["title", "description"]
    queryset = Position.objects.all()

    def filter_queryset(self, queryset):
        return (
            super()
            .filter_queryset(queryset)
            .filter(professor__id=self.request.user.professor.id)
        )


class ProfessorOtherPositionFilteringViewSet(ListModelMixin, GenericViewSet):
    serializer_class = ProfessorPositionListSerializer
    permission_classes = [IsAuthenticated, IsProfessor]
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    filterset_class = ProfessorOtherPositionFilter
    queryset = Position.objects.all()
    ordering_fields = ["fee", "position_start_date"]

    def filter_queryset(self, queryset):
        return (
            super()
            .filter_queryset(queryset)
            .exclude(professor__id=self.request.user.professor.id)
        )


class StudentPositionFilteringViewSet(ListModelMixin, GenericViewSet):
    serializer_class = StudentPositionListSerializer
    permission_classes = [IsAuthenticated, IsStudent]
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    filterset_class = StudentPositionFilter
    queryset = Position.objects.all()
    ordering_fields = ["fee", "position_start_date"]


# Request Filtering Views ------------------------------------------------------


class StudentRequestFilteringViewSet(ListModelMixin, GenericViewSet):
    serializer_class = RequestListSeralizer
    permission_classes = [IsAuthenticated, IsStudent, IsRequestOwner]
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    filterset_class = StudentRequestFilter
    ordering_fields = ["fee", "position_start_date", "date_applied"]
    queryset = (
        Request.objects.select_related("student").order_by("date_applied").reverse()
    )

    def filter_queryset(self, queryset):
        return (
            super()
            .filter_queryset(queryset)
            .filter(student__id=self.request.user.student.id)
        )


class ProfessorRequestFilteringViewSet(ListModelMixin, GenericViewSet):
    serializer_class = RequestListSeralizer
    permission_classes = [IsAuthenticated, IsProfessor, IsRequestOwner]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProfessorRequestFilter
    queryset = (
        Request.objects.select_related("position", "student")
        .order_by("date_applied")
        .reverse()
    )

    def filter_queryset(self, queryset):
        return (
            super()
            .filter_queryset(queryset)
            .filter(position__professor__id=self.request.user.professor.id)
        )


# CV Views ---------------------------------------------------------------------


class CVAPIView(APIView):
    name = "CV API"
    serializer_class = CVSerializer

    def get(self, request, format=None, **kwargs):
        cv = self.get_object()
        serializer = CVSerializer(cv)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, format=None, **kwargs):
        cv = self.get_object()
        serializer = CVSerializer(cv, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self):
        kws = self.kwargs
        if "professor_pk" in kws:
            return get_object_or_404(CV, professor_id=kws["professor_pk"])
        if "student_pk" in kws:
            return get_object_or_404(CV, student_id=kws["student_pk"])
        raise Http404("No CV matches the given query.")

    def get_permissions(self):
        if self.request.method.lower() == "get":
            return [AllowAny()]
        if self.request.method.lower() in ["patch", "put", "delete"]:
            return [IsAuthenticated(), IsCVOwner()]
        return [AllowAny()]


class BaseCVItemViewSet(
    CreateModelMixin,
    UpdateModelMixin,
    ListModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    def get_queryset(self):
        kws = self.kwargs
        if "professor_pk" in kws:
            return self.model.objects.filter(cv__professor__pk=kws["professor_pk"])
        elif "student_pk" in kws:
            return self.model.objects.filter(cv__student__pk=kws["student_pk"])
        else:
            raise Http404("No CV matches the given query.")

    def perform_create(self, serializer):
        cv = self.get_cv()
        serializer.save(cv=cv)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsCVOwnerNested()]
        return [AllowAny()]

    def get_cv(self):
        kws = self.kwargs
        if "professor_pk" in kws:
            return get_object_or_404(CV, professor_id=kws["professor_pk"])
        if "student_pk" in kws:
            return get_object_or_404(CV, student_id=kws["student_pk"])
        raise Http404("No CV matches the given query.")


class WorkExperienceViewSet(BaseCVItemViewSet):
    serializer_class = WorkExperienceSerializer
    model = WorkExperience


class EducationHistoryViewSet(BaseCVItemViewSet):
    serializer_class = EducationHistorySerializer
    model = EducationHistory


class ProjectExperienceViewSet(BaseCVItemViewSet):
    serializer_class = ProjectExperienceSerializer
    model = ProjectExperience


class HardSkillViewSet(BaseCVItemViewSet):
    serializer_class = HardSkillSerializer
    model = HardSkill


class LanguageSkillViewSet(BaseCVItemViewSet):
    serializer_class = LanguageSkillSerializer
    model = LanguageSkill


# Notification Views -----------------------------------------------------------


class NotificationViewSet(
    RetrieveModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    GenericViewSet,
):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, IsNotificationOwner]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).prefetch_related(
            "items"
        )

    @action(detail=False, methods=["GET"])
    def all_count(self, request):
        count = self.get_queryset().count()
        return Response({"count": count})

    @action(detail=False, methods=["GET"])
    def new_count(self, request):
        count = self.get_queryset().filter(read=False).count()
        return Response({"count": count})

    @action(detail=False, methods=["GET"])
    def new_notifications(self, request):
        notifications = self.get_queryset().filter(read=False)
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["GET"])
    def all_notifications(self, request):
        notifications = self.get_queryset()
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["GET"])
    def bookmarked_notifications(self, request):
        notifications = self.get_queryset().filter(bookmarked=True)
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["GET"])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.read = True
        notification.save()
        serializer = self.get_serializer(notification)
        return Response(serializer.data)

    @action(detail=False, methods=["GET"])
    def read_all(self, request):
        unread_notifications = self.get_queryset().filter(read=False)
        unread_notifications.update(read=True)
        return Response({"detail": "All notifications have been marked as read."})

    @action(detail=True, methods=["GET"])
    def toggle_bookmark(self, request, pk=None):
        notification = self.get_object()
        notification.bookmarked = not notification.bookmarked
        notification.save()
        return Response(
            {
                "detail": f"Notification bookmarked status changed to {notification.bookmarked}."
            }
        )

    @action(detail=False, methods=["GET"])
    def delete_all(self, request):
        notifications = self.get_queryset().filter(bookmarked=False)
        count = notifications.count()
        notifications.delete()
        return Response(
            {"detail": f"{count} unbookmarked notifications have been deleted."}
        )


# Top 5 Students ViewSet -------------------------------------------------------


class Top5StudentsViewSet(ListModelMixin, GenericViewSet):
    serializer_class = Top5StudentsSerializer
    permission_classes = [IsAuthenticated, IsProfessor]

    def list(self, request, *args, **kwargs):
        educations_with_date = EducationHistory.objects.exclude(end_date__isnull=True)

        cvs_with_avg_grade = (
            CV.objects.select_related("student")
            .filter(student__major=request.user.professor.major)
            .filter(education_histories__in=educations_with_date)
            .annotate(avg_grade=Avg("education_histories__grade"))
        )

        top_cvs = cvs_with_avg_grade.order_by("-avg_grade")[:5]

        top_students = (
            Student.objects.select_related("cv")
            .filter(major__isnull=False)
            .filter(major=request.user.professor.major)
            .filter(cv__in=top_cvs)
        )

        seralizer = Top5StudentsSerializer(top_students, many=True)

        return Response(seralizer.data)


class Top5ProfessorsViewSet(ListModelMixin, GenericViewSet):
    serializer_class = Top5ProfessorsSerializer
    permission_classes = [IsAuthenticated, IsStudent]

    def list(self, request, *args, **kwargs):
        top_professors = (
            Professor.objects.filter(major__isnull=False)
            .filter(major=request.user.student.major)
            .select_related("cv")
            .annotate(project_num=Count("cv__project_experiences"))
            .order_by("-project_num")[:5]
        )

        seralizer = Top5ProfessorsSerializer(top_professors, many=True)

        return Response(seralizer.data)
