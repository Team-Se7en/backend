from rest_framework.permissions import BasePermission


class IsProfessor(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (not request.user.is_student)
        )


class IsPositionOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.professor.id == obj.professor.id


class AllowNone(BasePermission):
    def has_permission(self, request, view):
        return False


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_student)


class IsRequestOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_student:
            return bool(request.user.student.id == obj.student.id)
        else:
            return bool(request.user.professor.id == obj.position.professor.id)
