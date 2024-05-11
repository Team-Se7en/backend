from django_filters import rest_framework as filters
from .models import Position


class ProfessorOwnPositionFilter(filters.FilterSet):
    term = filters.CharFilter(method="filter_by_season")
    fee = filters.NumberFilter()
    fee__gte = filters.NumberFilter(field_name="fee", lookup_expr="gte")
    fee__lte = filters.NumberFilter(field_name="fee", lookup_expr="lte")

    class Meta:
        model = Position
        fields = ["fee"]

    def filter_by_season(self, queryset, name, value):
        if value.lower() == "summer":
            return queryset.filter(your_field__gt=5, your_field__lt=9)
        elif value.lower() == "winter":
            return queryset.filter(your_field__gt=9, your_field__lt=12)
        elif value.lower() == "spring":
            return queryset.filter(your_field__gt=1, your_field__lt=5)
        else:
            return queryset
