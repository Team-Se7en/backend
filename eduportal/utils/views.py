from django.http import HttpRequest


def get_user_type(request: HttpRequest):
    user = request.user
    if user.is_anonymous:
        return "Anonymous"
    elif user.is_superuser:
        return "Admin"
    elif user.is_staff:
        return "Staff"
    elif user.is_student:
        return "Student"
    else:
        return "Professor"
