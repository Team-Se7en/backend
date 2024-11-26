import base64
from django.http import HttpRequest


def get_user_type(request: HttpRequest):
    user = request.user
    if user.is_anonymous:
        return "Anonymous"
    # elif user.is_superuser:
    #     return "Admin"
    # elif user.is_staff:
    #     return "Staff"
    elif user.is_student:
        return "Student"
    else:
        return "Professor"


def get_image_base64(image):
    if image:
        with open(image.path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
    return None
