from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    is_admin = models.BooleanField(default=True)  # or False for customers later
    # Add phone, address if needed
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)