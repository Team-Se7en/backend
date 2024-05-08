from eduportal.models import SoftSkill
from .field_choices import SoftSkillChoices

def update_soft_skills():
    SoftSkill.objects.all().delete()

    for skill in SoftSkillChoices:
        SoftSkill.objects.create(skill=skill)
