# Generated by Django 3.0.7 on 2020-07-26 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='boardmodel',
            name='game_id',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]