from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    def paginate_queryset(self, queryset, request, view=None):
        if "page" in request.query_params:
            return super().paginate_queryset(queryset, request, view)
        else:
            return None

    def get_paginated_response(self, data):
        if self.page is not None:
            response = super().get_paginated_response(data)
            response.data["total_pages"] = self.page.paginator.num_pages
            return response
        else:
            return Response(data)


class PaginatedActionMixin:
    def paginated_action(self, queryset, serializer_class):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = serializer_class(queryset, many=True)
        return Response(serializer.data)
