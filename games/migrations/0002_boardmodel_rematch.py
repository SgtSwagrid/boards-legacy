# Generated by Django 3.0.8 on 2020-08-03 16:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='boardmodel',
            name='rematch',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='games.BoardModel'),
        ),
    ]