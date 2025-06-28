from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager

class Occupation(models.TextChoices):
    STUDENT_UNDERGRADUATE = 'student_undergraduate', 'Student - Undergraduate'
    STUDENT_GRADUATE = 'student_graduate', 'Student - Graduate'
    FACULTY = 'faculty', 'Faculty'
    ALUMNI = 'alumni', 'Alumni'
    OTHER = 'other', 'Other'


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(email, password, **extra_fields)

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
    
    objects = CustomUserManager()








