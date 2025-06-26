from django.db import models
from django.contrib.auth.models import AbstractUser

class Occupation(models.TextChoices):
    STUDENT_UNDERGRADUATE = 'student_undergraduate', 'Student - Undergraduate'
    STUDENT_GRADUATE = 'student_graduate', 'Student - Graduate'
    FACULTY = 'faculty', 'Faculty'
    ALUMNI = 'alumni', 'Alumni'
    OTHER = 'other', 'Other'

class CustomUser(AbstractUser):
    # Remove Username Field
    username = None

    # Setup Email for auth
    email = models.EmailField(max_length=100, unique=True)
    USERNAME_FIELD = 'email'

    country = models.CharField(max_length=25)
    organization = models.CharField(max_length=25)
    phone = models.CharField(max_length=15)
    occupation = models.CharField(max_length=50, choices=Occupation.choices, default=Occupation.STUDENT_UNDERGRADUATE)

    iatm_membership = models.BooleanField(default=False)


    REQUIRED_FIELDS = ['first_name', 'last_name', 'country', 'organization', 'phone', 'occupation']







