from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

# User has the follow attributes
# username, email, first_name, last_name,password, is_active, is_staff,
# is_superuser, groups, user_permissions, last_login, date_joined language
class User(AbstractUser):
    email = models.EmailField(unique=True)
    language = models.CharField(max_length=5, default="en")