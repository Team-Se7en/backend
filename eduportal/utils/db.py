from eduportal.models import SoftSkill
from eduportal.models import Student, Professor, CV
from .field_choices import SoftSkillChoices


def update_soft_skills():
    SoftSkill.objects.all().delete()

    for skill in SoftSkillChoices:
        SoftSkill.objects.create(skill=skill)


def create_missing_cvs():
    for professor in Professor.objects.all():
        if not hasattr(professor, "cv"):
            CV.objects.create(professor=professor)

    for student in Student.objects.all():
        if not hasattr(student, "cv"):
            CV.objects.create(student=student)
