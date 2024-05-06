from django.contrib.auth import get_user_model
from django.db.models import Prefetch, Min
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from pprint import pprint
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
        top_universities = University.objects.order_by("rank")[:5]
        serializer = UniversitySerializer(top_universities, many=True)

        return serializer.data

    def top_professors(self, request):
        professors = Professor.objects.annotate(
            accepted_requests_count=models.Count(
                "positions__request", filter=models.Q(positions__request__status="A")
            )
        ).select_related("user")

        top_professors = professors.order_by("-accepted_requests_count")[:5]

        data = []
        for prof in top_professors:
            serializer = ProfessorSerializer(prof)
            data.append((serializer.data, prof.accepted_requests_count))

        return data

    def top_students(self, request):
        students = Student.objects.annotate(
            accepted_requests_count=models.Count(
                "request", filter=models.Q(request__status="A")
            )
        ).select_related("user")

        top_students = students.order_by("-accepted_requests_count")[:5]

        data = []
        for student in top_students:
            serializer = StudentGetListSerializer(student)
            data.append((serializer.data, student.accepted_requests_count))

        return data


# User Views -------------------------------------------------------------------


class UserInfoViewSet(GenericViewSet):
    def list(self, request):
        user = request.user
        serializer = UserDetailSerializer(user, context={"request": self.request})
        return Response(serializer.data)


# University Views -------------------------------------------------------------


class UniversityViewSet(ModelViewSet):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer

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
    search_fields = ["user__first_name", "user__last_name", "university_name"]


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
    search_fields = [
        "department",
        "university__name",
        "user__first_name",
        "user__last_name",
    ]

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
        ).prefetch_related("tags")
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
        ).prefetch_related("tags")
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
        ).prefetch_related("tags")

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


class RequestViewSet(ModelViewSet):
    http_method_names = ["post", "get", "patch", "delete"]

    def get_queryset(self):
        return Request.objects.all()

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), IsStudent()]
        if self.action == "list":
            return [IsAuthenticated()]
        if self.action in ["partial_update", "update"]:
            return [IsAuthenticated(), IsProfessor(), IsRequestOwner()]
        if self.action == "destroy":
            return [AllowNone()]
        if self.action == "retrieve":
            return [IsAuthenticated(), IsRequestOwner()]
        return [AllowNone()]

    def get_serializer_class(self):
        if self.action == "create":
            return StudentCreateRequestSerializer
        if self.action in ["update", "partial_update"]:
            return ProfessorRequestUpdateSeralizer
        if self.action == "retrieve":
            if self.request.user.is_student:
                return StudentRequestDetailSerializer
            else:
                return ProfessorRequestDetailSerializer
        if self.action == "list":
            return RequestListSeralizer
        return RequestListSeralizer

    def destroy(self, request, *args, **kwargs):
        request_object = get_object_or_404(Request, pk=kwargs["pk"])
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
        if position.capacity == 0:
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
        position = serializer.save()
        serializer = StudentCreateRequestSerializer(position)
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
        request_object = get_object_or_404(Request, pk=kwargs["pk"])
        if request_object.status != "A":
            return Response("Invalid admission.", status=status.HTTP_400_BAD_REQUEST)
        request_object.share_with_others = True
        return super().update(request, *args, **kwargs)


# Position Filtering Views -----------------------------------------------------


class ProfessorOwnPositionFilteringViewSet(ListModelMixin, GenericViewSet):
    serializer_class = ProfessorPositionListSerializer
    permission_classes = [IsAuthenticated, IsProfessor, IsPositionOwner]
    filter_backends = [OrderingFilter]
    ordering_fields = ["request_count", "fee", "position_start_date"]

    def get_queryset(self):
        base_query = Position.objects.select_related("professor").filter(
            professor__id=self.request.user.professor.id
        )
        # if self.request.query_params.get('ordering'):
        #    if 'position_start_date' in self.request.query_params['ordering']:
        #        base_query = base_query.filter(
        #        position_start_date__gte=timezone.now().date()
        #        )
        filter_options = self.request.query_params
        min_fee = filter_options.get("min_fee")
        max_fee = filter_options.get("max_fee")
        term = filter_options.get("term")
        year = filter_options.get("year")
        if min_fee is not None:
            base_query = base_query.filter(fee__gte=min_fee)
        if max_fee is not None:
            base_query = base_query.filter(fee__lte=max_fee)
        if term is not None:
            if term == "summer":
                base_query = base_query.filter(
                    position_start_date__month__gte=5
                ).filter(position_start_date__month__lt=10)
            elif term == "winter":
                base_query = base_query.filter(
                    position_start_date__month__gte=10
                ).filter(position_start_date__month__lte=12)
            elif term == "spring":
                base_query = base_query.filter(
                    position_start_date__month__gte=1
                ).filter(position_start_date__month__lt=5)
            else:
                return Response("Invalid Term", status=status.HTTP_400_BAD_REQUEST)
        if year is not None:
            base_query = base_query.filter(position_start_date__year=year)
        return base_query


class ProfessorOtherPositionFilteringViewSet(ListModelMixin, GenericViewSet):
    serializer_class = ProfessorPositionListSerializer
    permission_classes = [IsAuthenticated, IsProfessor]
    filter_backends = [OrderingFilter]
    ordering_fields = ["fee", "position_start_date"]

    def get_queryset(self):
        base_query = Position.objects.select_related("professor").exclude(
            professor__id=self.request.user.professor.id
        )
        # if self.request.query_params.get('ordering'):
        #    if 'position_start_date' in self.request.query_params['ordering']:
        #        base_query = base_query.filter(
        #        position_start_date__gte=timezone.now().date()
        #        )
        filter_options = self.request.query_params
        min_fee = filter_options.get("min_fee")
        max_fee = filter_options.get("max_fee")
        term = filter_options.get("term")
        year = filter_options.get("year")
        if min_fee is not None:
            base_query = base_query.filter(fee__gte=min_fee)
        if max_fee is not None:
            base_query = base_query.filter(fee__lte=max_fee)
        if term is not None:
            if term == "summer":
                base_query = base_query.filter(
                    position_start_date__month__gte=5
                ).filter(position_start_date__month__lt=10)
            elif term == "winter":
                base_query = base_query.filter(
                    position_start_date__month__gte=10
                ).filter(position_start_date__month__lte=12)
            elif term == "spring":
                base_query = base_query.filter(
                    position_start_date__month__gte=1
                ).filter(position_start_date__month__lt=5)
            else:
                return Response("Invalid Term", status=status.HTTP_400_BAD_REQUEST)
        if year is not None:
            base_query = base_query.filter(position_start_date__year=year)
        return base_query


class StudentPositionFilteringViewSet(ListModelMixin, GenericViewSet):
    serializer_class = StudentPositionListSerializer
    permission_classes = [IsAuthenticated, IsStudent]
    filter_backends = [OrderingFilter]
    ordering_fields = ["fee", "position_start_date"]

    def get_queryset(self):
        base_query = Position.objects.all()
        filter_options = self.request.query_params
        min_fee = filter_options.get("min_fee")
        max_fee = filter_options.get("max_fee")
        term = filter_options.get("term")
        year = filter_options.get("year")
        is_filled = filter_options.get("is_filled")
        if min_fee is not None:
            base_query = base_query.filter(fee__gte=min_fee)
        if max_fee is not None:
            base_query = base_query.filter(fee__lte=max_fee)
        if term is not None:
            if term == "summer":
                base_query = base_query.filter(
                    position_start_date__month__gte=5
                ).filter(position_start_date__month__lt=10)
            elif term == "winter":
                base_query = base_query.filter(
                    position_start_date__month__gte=10
                ).filter(position_start_date__month__lte=12)
            elif term == "spring":
                base_query = base_query.filter(
                    position_start_date__month__gte=1
                ).filter(position_start_date__month__lt=5)
            else:
                return Response("Invalid Term", status=status.HTTP_400_BAD_REQUEST)
        if year is not None:
            base_query = base_query.filter(position_start_date__year=year)
        if is_filled is not None:
            if is_filled == "Y":
                base_query = base_query.filter(filled=1)
            elif is_filled == "N":
                base_query = base_query.filter(filled=0)
            else:
                return Response(
                    "Invalid filled value", status=status.HTTP_400_BAD_REQUEST
                )
        return base_query


# Request Filtering Views ------------------------------------------------------


class StudentRequestFilteringViewSet(ListModelMixin, GenericViewSet):
    serializer_class = RequestListSeralizer
    permission_classes = [IsAuthenticated, IsStudent, IsRequestOwner]
    filter_backends = [OrderingFilter]
    ordering_fields = ["fee", "position_start_date", "date_applied"]

    def get_queryset(self):
        base_query = (
            Request.objects.select_related("student")
            .filter(student__id=self.request.user.student.id)
            .order_by("date_applied")
            .reverse()
        )
        filter_options = self.request.query_params
        min_fee = filter_options.get("min_fee")
        max_fee = filter_options.get("max_fee")
        term = filter_options.get("term")
        year = filter_options.get("year")
        status = filter_options.get("status")
        if min_fee is not None:
            base_query = base_query.filter(fee__gte=min_fee)
        if max_fee is not None:
            base_query = base_query.filter(fee__lte=max_fee)
        if term is not None:
            if term == "summer":
                base_query = base_query.filter(
                    position_start_date__month__gte=5
                ).filter(position_start_date__month__lt=10)
            elif term == "winter":
                base_query = base_query.filter(
                    position_start_date__month__gte=10
                ).filter(position_start_date__month__lte=12)
            elif term == "spring":
                base_query = base_query.filter(
                    position_start_date__month__gte=1
                ).filter(position_start_date__month__lt=5)
            else:
                return Response("Invalid Term", status=status.HTTP_400_BAD_REQUEST)
        if year is not None:
            base_query = base_query.filter(position_start_date__year=year)
        if status is not None:
            status_word = None
            if status == "A":
                status_word = "A"
            elif status == "P":
                status_word = "P"
            elif status == "R":
                status_word = "R"
            if status_word is None:
                return Request.objects.none()
            base_query = base_query.filter(status=status_word)
        return base_query


class ProfessorRequestFilteringViewSet(ListModelMixin, GenericViewSet):
    serializer_class = RequestListSeralizer
    permission_classes = [IsAuthenticated, IsProfessor, IsRequestOwner]

    def get_queryset(self):
        base_query = (
            Request.objects.select_related("position", "student")
            .filter(position__professor__id=self.request.user.professor.id)
            .order_by("date_applied")
            .reverse()
        )
        filter_options = self.request.query_params
        status = filter_options.get("status")
        major = filter_options.get("major")
        if status is not None:
            status_word = None
            if status == "A":
                status_word = "A"
            elif status == "P":
                status_word = "P"
            elif status == "R":
                status_word = "R"
            if status_word is None:
                return Request.objects.none()
            base_query = base_query.filter(status=status_word)
        if major is not None:
            base_query = base_query.filter(student__major=major)
        return base_query


# CV Views ---------------------------------------------------------------------


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class CVAPIView(APIView):
    name = "CV API"
    serializer_class = CVSerializer

    def get(self, request, professor_pk, format=None):
        cv = self.get_object(professor_pk)
        serializer = CVSerializer(cv)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, professor_pk, format=None):
        cv = self.get_object(professor_pk)
        serializer = CVSerializer(cv, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, professor_pk):
        get_object_or_404(CV, professor_id=professor_pk)
        return CV.objects.get(professor__id=professor_pk)

    def get_permissions(self):
        if self.request.method.lower() == "get":
            return [AllowAny()]
        if self.request.method.lower() in ["patch", "put", "delete"]:
            return [IsProfessor(), IsCVOwner()]
        return [AllowAny()]


class WorkExperienceViewSet(viewsets.ModelViewSet):
    queryset = WorkExperience.objects.all()
    # serializer_class = WorkExperienceSerializer


class EducationHistoryViewSet(viewsets.ModelViewSet):
    queryset = EducationHistory.objects.all()
    # serializer_class = EducationHistorySerializer


class HardSkillViewSet(viewsets.ModelViewSet):
    queryset = HardSkill.objects.all()
    # serializer_class = HardSkillSerializer


class SoftSkillViewSet(viewsets.ModelViewSet):
    queryset = SoftSkill.objects.all()
    # serializer_class = SoftSkillSerializer


class ProjectExperienceViewSet(viewsets.ModelViewSet):
    queryset = ProjectExperience.objects.all()
    # serializer_class = ProjectExperienceSerializer
