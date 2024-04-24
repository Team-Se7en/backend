from rest_framework.permissions import BasePermission

class IsProfessor(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (not request.user.is_student)
        )


class IsPositionOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.id == obj.professor.user.id)
        )


class AllowNone(BasePermission):
    def has_permission(self, request, view):
        return False

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_student)
