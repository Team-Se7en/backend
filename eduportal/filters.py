from django_filters.rest_framework import FilterSet, CharFilter, NumberFilter
from .models import Position


class ProfessorOwnPositionFilter(FilterSet):
    term = CharFilter(method="filter_by_season")
    fee__gte = NumberFilter(field_name="fee", lookup_expr="gte")
    fee__lte = NumberFilter(field_name="fee", lookup_expr="lte")

    class Meta:
        model = Position
        fields = ["position_start_date__year"]

    def filter_by_season(self, queryset, name, value):
        if value == "spring":
            return queryset.filter(
                position_start_date__month__gte=1, position_start_date__month__lte=5
            )
        elif value == "summer":
            return queryset.filter(
                position_start_date__month__gte=6, position_start_date__month__lt=10
            )
        elif value == "winter":
            return queryset.filter(
                position_start_date__month__gte=10, position_start_date__month__lte=12
            )
        elif value is None:
            return queryset
        else:
            return queryset.none()
