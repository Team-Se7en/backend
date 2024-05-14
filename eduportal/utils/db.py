from eduportal.models import SoftSkill, Tag2
from eduportal.models import Student, Professor, CV
from .field_choices import SoftSkillChoices, TagChoices


def update_soft_skills():
    SoftSkill.objects.all().delete()

    for skill in SoftSkillChoices:
        SoftSkill.objects.create(skill=skill)


def update_tags():
    Tag2.objects.all().delete()

    for tag in TagChoices:
        Tag2.objects.create(label=tag)


def create_missing_cvs():
    for professor in Professor.objects.all():
        if not hasattr(professor, "cv"):
            CV.objects.create(professor=professor)

    for student in Student.objects.all():
        if not hasattr(student, "cv"):
            CV.objects.create(student=student)
