# Generated by Django 4.0.4 on 2022-05-21 19:30

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Users',
            fields=[
                ('username', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('userid', models.IntegerField(unique=True)),
                ('password', models.CharField(max_length=64)),
                ('salt', models.CharField(max_length=64)),
            ],
        ),
    ]
