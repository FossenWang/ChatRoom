from django.db import models


class Room(models.Model):
    name = models.CharField(max_length=20)
    max_number = models.PositiveIntegerField('最大聊天人数', default=10)

    def __str__(self):
        return self.name
