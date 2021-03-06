# Generated by Django 4.0.4 on 2022-05-19 18:54

import datetime
import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sku', models.CharField(max_length=15)),
                ('quantity', models.IntegerField()),
                ('store', models.CharField(max_length=3)),
                ('store_id', models.CharField(max_length=8)),
                ('check_time', models.DateTimeField(default=datetime.datetime.utcnow)),
            ],
        ),
        migrations.CreateModel(
            name='Products',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('userid', models.IntegerField()),
                ('sku', models.CharField(max_length=15)),
                ('name', models.CharField(max_length=64)),
                ('store', models.CharField(max_length=3)),
                ('track', models.IntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='Stores',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('store', models.CharField(max_length=3)),
                ('store_id', models.CharField(max_length=8)),
                ('store_name', models.CharField(max_length=48)),
                ('address', models.CharField(max_length=96)),
                ('city', models.CharField(max_length=24)),
                ('state', models.CharField(max_length=24)),
                ('zipcode', models.CharField(max_length=5)),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326)),
            ],
        ),
        migrations.CreateModel(
            name='Zipcodes',
            fields=[
                ('userid', models.IntegerField(primary_key=True, serialize=False)),
                ('zipcode', models.CharField(default='00000', max_length=5)),
            ],
        ),
        migrations.CreateModel(
            name='ZipcodeStoresMapping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('store', models.CharField(max_length=3)),
                ('zipcode', models.CharField(max_length=5)),
                ('store_id', models.CharField(max_length=8)),
            ],
        ),
        migrations.AddConstraint(
            model_name='zipcodestoresmapping',
            constraint=models.UniqueConstraint(fields=('store', 'zipcode', 'store_id'), name='unique_store_zipcode_storeID'),
        ),
        migrations.AddConstraint(
            model_name='stores',
            constraint=models.UniqueConstraint(fields=('store', 'store_id'), name='unique_store_storeID'),
        ),
        migrations.AddConstraint(
            model_name='products',
            constraint=models.UniqueConstraint(fields=('userid', 'sku', 'store'), name='unique_userid_sku_store'),
        ),
        migrations.AddConstraint(
            model_name='inventory',
            constraint=models.UniqueConstraint(fields=('sku', 'store', 'store_id'), name='unique_sku_store_storeID'),
        ),
    ]
