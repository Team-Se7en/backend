from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsProfessor(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (not request.user.is_student)
        )


class IsCVOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        user_id = request.user.id
        if obj.professor:
            return user_id == obj.professor.user.id
        elif obj.student:
            return user_id == obj.student.user.id

        return False


class IsCVOwnerNested(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if user.is_student:
            if "student_pk" in view.kwargs:
                return user.student.id == int(view.kwargs["student_pk"])
            else:
                return False
        else:
            if "professor_pk" in view.kwargs:
                return user.professor.id == int(view.kwargs["professor_pk"])
            else:
                return False


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


class IsNotificationOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
    
class IsOwnMessage(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.user is None:
            return False
        if obj.user.id == request.user.id:
            return True
        return False
