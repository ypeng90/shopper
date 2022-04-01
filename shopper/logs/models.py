# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from decimal import Decimal


class Extras(models.Model):
    no = models.AutoField(primary_key=True)
    sku = models.CharField(max_length=15)
    offset = models.IntegerField(default=0)
    aisle = models.CharField(max_length=20, default='')
    note = models.CharField(max_length=100, default='')
    store = models.CharField(max_length=3)
    location_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'extras'
        unique_together = (('sku', 'store', 'location_id'),)
        verbose_name_plural = 'Extras'


class Stores(models.Model):
    no = models.AutoField(primary_key=True)
    store = models.CharField(max_length=3)
    location_id = models.IntegerField()
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=30)
    state = models.CharField(max_length=2)
    zipcode = models.CharField(max_length=10)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    tax = models.DecimalField(max_digits=6, decimal_places=5, default=Decimal('0.00000'))

    class Meta:
        managed = False
        db_table = 'stores'
        unique_together = (('store', 'location_id'),)
        verbose_name_plural = 'Stores'
