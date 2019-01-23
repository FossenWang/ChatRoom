from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    avatar = models.URLField(max_length=200, null=True, blank=True, verbose_name='头像')


class Room(models.Model):
    name = models.CharField(max_length=20)
    max_number = models.PositiveIntegerField('最大聊天人数', default=10)

    def __str__(self):
        return self.name
