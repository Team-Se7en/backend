from django.db import models


class TagChoices(models.IntegerChoices):
    ARTIFICIAL_INTELLIGENCE = 1
    DATA_SCIENCE = 2
    MACHINE_LEARNING = 3
    CYBER_SECURITY = 4
    SOFTWARE_ENGINEERING = 5
    CLOUD_COMPUTING = 6
    QUANTUM_COMPUTING = 7


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


class LanguageChoices(models.IntegerChoices):
    MANDARIN_CHINESE = 1
    SPANISH = 2
    ENGLISH = 3
    HINDI = 4
    BENGALI = 5
    PORTUGUESE = 6
    RUSSIAN = 7
    JAPANESE = 8
    WESTERN_PUNJABI = 9
    MARATHI = 10
    TELUGU = 11
    WU_CHINESE = 12
    TURKISH = 13
    KOREAN = 14
    FRENCH = 15
    GERMAN = 16
    VIETNAMESE = 17
    TAMIL = 18
    YUE_CHINESE = 19
    URDU = 20
    JAVANESE = 21
    ITALIAN = 22
    ARABIC = 23
    GUJARATI = 24
    PERSIAN = 25
    BHOJPURI = 26
    SOUTHERN_MIN = 27
    HAKKA = 28
    JINYU_CHINESE = 29
    HAUSA = 30


class NotificationTypeChoices(models.IntegerChoices):
    STUDENT_CREATED_REQUEST = 1
    PROFESSOR_ACCEPTED_REQUEST = 2
    PROFESSOR_REJECTED_REQUEST = -2
    STUDENT_ACCEPTED_REQUEST = 3
    STUDENT_REJECTED_REQUEST = -3
    NEW_TAGGED_POST = 4


class MajorTypeChoices(models.IntegerChoices):
    COMPUTER_ENGINEERING = 1 
    SOFTWARE_ENGINEERING = 2 
    MECHANICAL_ENGINEERING = 3 
    ELECTRICAL_ENGINEERING = 4 
    CIVIL_ENGINEERING = 5 
    AEROSPACE_ENGINEERING = 6 
    BIOLOGY = 7 
    CHEMISTRY = 8 
    PHYSICS = 9 
    MATHEMATICS = 10 
    STATISTICS = 11 
    ECONOMICS = 12 
    PSYCHOLOGY = 13 
    SOCIOLOGY = 14 
    POLITICAL_SCIENCE = 15 
    PHILOSOPHY = 16 
    ENGLISH = 17 
    HISTORY = 18 
    ART = 19 
    MUSIC = 20 
    THEATRE = 21 
    EDUCATION = 22 
    BUSINESS = 23 
    ACCOUNTING = 24 
    FINANCE = 25 
    MARKETING = 26 
    HUMAN_RESOURCE_MANAGEMENT = 27 
    INTERNATIONAL_BUSINESS = 28 
    ENTREPRENEURSHI = 29 
