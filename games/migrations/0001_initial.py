# Generated by Django 3.0.8 on 2020-08-06 18:46

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ActionModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.IntegerField()),
                ('x_from', models.IntegerField(default=-1)),
                ('y_from', models.IntegerField(default=-1)),
                ('x_to', models.IntegerField(default=-1)),
                ('y_to', models.IntegerField(default=-1)),
                ('option', models.IntegerField(default=-1)),
            ],
            managers=[
                ('actions', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='BoardModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game_id', models.IntegerField()),
                ('code', models.CharField(max_length=5)),
                ('status', models.IntegerField(default=0)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('rematch', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='games.BoardModel')),
            ],
            options={
                'ordering': ['-time'],
            },
            managers=[
                ('boards', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='StateModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game_id', models.IntegerField()),
                ('current', models.IntegerField(default=0)),
                ('stage', models.IntegerField(default=0)),
                ('ply', models.IntegerField(default=0)),
                ('epoch', models.IntegerField(default=0)),
                ('outcome', models.IntegerField(default=-2)),
                ('action', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='games.ActionModel')),
                ('previous', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='games.StateModel')),
            ],
            managers=[
                ('states', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='PlayerStateModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField()),
                ('score', models.IntegerField(default=0)),
                ('mode', models.IntegerField(default=0)),
                ('state', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='games.StateModel')),
            ],
            options={
                'ordering': ['state', 'order'],
            },
            managers=[
                ('players', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='PlayerModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField()),
                ('score', models.IntegerField(default=0)),
                ('leader', models.BooleanField(default=False)),
                ('time', models.TimeField(default=datetime.time(0, 0))),
                ('forfeited', models.BooleanField(default=False)),
                ('board', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='games.BoardModel')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['board', 'order'],
            },
        ),
        migrations.CreateModel(
            name='PieceModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.IntegerField()),
                ('owner', models.IntegerField()),
                ('x', models.IntegerField()),
                ('y', models.IntegerField()),
                ('mode', models.IntegerField(default=0)),
                ('state', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='games.StateModel')),
            ],
            options={
                'ordering': ['state'],
            },
            managers=[
                ('pieces', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='ChangeModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('x', models.IntegerField()),
                ('y', models.IntegerField()),
                ('state', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='games.StateModel')),
            ],
            managers=[
                ('changes', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AddField(
            model_name='boardmodel',
            name='state',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='games.StateModel'),
        ),
    ]
