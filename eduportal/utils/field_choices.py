from django.db import models


class GenderChoices(models.IntegerChoices):
    MALE = 1
    FEMALE = 2
    RATHER_NOT_SAY = 3


class EmploymentStatusChoices(models.IntegerChoices):
    EMPLOYED = 1
    UNEMPLOYED = 2
    STUDENT = 3
    ACTIVELY_SEEKING_WORK = 4
    OPEN_TO_WORK = 5
    NOT_INTERESTED = 6


class SoftSkillChoices(models.IntegerChoices):
    COMMUNICATION = 1
    TEAMWORK = 2
    PROBLEM_SOLVING = 3


class TechChoices(models.IntegerChoices):
    PYTHON = 1
    DJANGO = 2
    FLASK = 3
    JAVASCRIPT = 4
    REACT = 5
    ANGULAR = 6
    VUE = 7
    JAVA = 8
    SPRING = 9
    HIBERNATE = 10
    C = 11
    CPP = 12
    CSHARP = 13
    DOTNET = 14
    RUBY = 15
    RAILS = 16
    PHP = 17
    LARAVEL = 18
    SWIFT = 19
    KOTLIN = 20
    GO = 21
    RUST = 22
    SCALA = 23
    GROOVY = 24
    TYPESCRIPT = 25
    NODEJS = 26
    EXPRESS = 27
    RUBY_ON_RAILS = 28
    SQL = 29
    NOSQL = 30


class XPDurationChoices(models.IntegerChoices):
    LESS_THAN_A_YEAR = 1
    BETWEEN_1_AND_5_YEARS = 2
    MORE_THAN_5_YEARS = 3
