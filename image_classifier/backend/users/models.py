from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    is_premium = models.BooleanField(default=False)

    full_name = models.CharField(max_length=255, default='Не указан')
    position = models.CharField(max_length=255, default='Не указан')
    district = models.CharField(max_length=255, default='Не указан')





