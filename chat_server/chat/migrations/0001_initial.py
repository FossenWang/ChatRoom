# Generated by Django 2.1.3 on 2019-01-11 15:59

from django.db import migrations, models


def initial_data(apps, schema_editor):
    from django.contrib.auth.models import User
    from chat.models import Room
    User.objects.create_superuser('admin', None, 'admin123')
    Room.objects.create(name='Test', max_number=10)
    for i in range(1, 6):
        User.objects.create_user(f'user{i}')
        Room.objects.create(name=f'Room{i}', max_number=(10 + i))


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('max_number', models.PositiveIntegerField(default=10, verbose_name='最大聊天人数')),
            ],
        ),
        migrations.RunPython(initial_data),
    ]
