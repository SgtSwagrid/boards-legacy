# Generated by Django 3.0.8 on 2020-08-27 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0005_auto_20200827_1156'),
    ]

    operations = [
        migrations.AddField(
            model_name='boardmodel',
            name='outcome',
            field=models.IntegerField(default=-2),
        ),
    ]
