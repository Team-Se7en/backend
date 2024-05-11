from django_filters import rest_framework as filters
from .models import Position


class ProfessorOwnPositionFilter(filters.FilterSet):
    term = filters.CharFilter(method="filter_by_season")
    # fee = filters.NumberFilter()
    # fee__gte = filters.NumberFilter(field_name="fee", lookup_expr="gte")
    # fee__lte = filters.NumberFilter(field_name="fee", lookup_expr="lte")

    class Meta:
        model = Position
        fields = {"fee": ["lte", "gte"], "position_start_date": ["year__exact"]}

    def filter_by_season(self, queryset, name, value):
        if value.lower() == "summer":
            return queryset.filter(
                position_start_date__month__gte=6, position_start_date__month__lte=9
            )
        elif value.lower() == "winter":
            return queryset.filter(
                position_start_date__month__gte=10, position_start_date__month__lte=12
            )
        elif value.lower() == "spring":
            return queryset.filter(
                position_start_date__month__gte=1, position_start_date__month__lte=5
            )
        elif value is None:
            return queryset
        else:
            return queryset.none()


class ProfessorOtherPositionFilter(filters.FilterSet):
    term = filters.CharFilter(method="filter_by_season")
    # fee = filters.NumberFilter()
    # fee__gte = filters.NumberFilter(field_name="fee", lookup_expr="gte")
    # fee__lte = filters.NumberFilter(field_name="fee", lookup_expr="lte")

    class Meta:
        model = Position
        fields = {"fee": ["lte", "gte"], "position_start_date": ["year__exact"]}

    def filter_by_season(self, queryset, name, value):
        if value.lower() == "summer":
            return queryset.filter(
                position_start_date__month__gte=6, position_start_date__month__lte=9
            )
        elif value.lower() == "winter":
            return queryset.filter(
                position_start_date__month__gte=10, position_start_date__month__lte=12
            )
        elif value.lower() == "spring":
            return queryset.filter(
                position_start_date__month__gte=1, position_start_date__month__lte=5
            )
        elif value is None:
            return queryset
        else:
            return queryset.none()


class StudentPositionFilter(filters.FilterSet):
    term = filters.CharFilter(method="filter_by_season")
    # fee = filters.NumberFilter()
    # fee__gte = filters.NumberFilter(field_name="fee", lookup_expr="gte")
    # fee__lte = filters.NumberFilter(field_name="fee", lookup_expr="lte")

    class Meta:
        model = Position
        fields = {
            "fee": ["lte", "gte"],
            "position_start_date": ["year__exact"],
            "filled": ["exact"],
        }

    def filter_by_season(self, queryset, name, value):
        if value.lower() == "summer":
            return queryset.filter(
                position_start_date__month__gte=6, position_start_date__month__lte=9
            )
        elif value.lower() == "winter":
            return queryset.filter(
                position_start_date__month__gte=10, position_start_date__month__lte=12
            )
        elif value.lower() == "spring":
            return queryset.filter(
                position_start_date__month__gte=1, position_start_date__month__lte=5
            )
        elif value is None:
            return queryset
        else:
            return queryset.none()
