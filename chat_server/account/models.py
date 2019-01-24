from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    avatar = models.URLField(max_length=200, null=True, blank=True, verbose_name='头像')
