from django.contrib.gis.db.models import PointField
from django.db import models
from datetime import datetime


# Create directly in MySQL
# CREATE TABLE products
# (
#     userid int NOT NULL,
#     sku varchar(15) NOT NULL,
#     name varchar(64) NOT NULL,
#     store char(3) NOT NULL,
#     track int NOT NULL DEFAULT 1,
#     PRIMARY KEY (userid, sku, store)
# );
class Products(models.Model):
    userid = models.IntegerField()
    sku = models.CharField(max_length=15)
    name = models.CharField(max_length=64)
    store = models.CharField(max_length=3)
    track = models.IntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["userid", "sku", "store"],
                name="unique_userid_sku_store"
            )
        ]


# CREATE TABLE zipcodes
# (
#     userid int NOT NULL,
#     zipcode char(5) NOT NULL DEFAULT '00000',
#     PRIMARY KEY (userid)
# );
class Zipcodes(models.Model):
    userid = models.IntegerField(primary_key=True)
    zipcode = models.CharField(max_length=5, default="00000")


# Create directly in MySQL
# CREATE TABLE inventory
# (
#     sku varchar(15) NOT NULL,
#     quantity int NOT NULL,
#     store char(3) NOT NULL,
#     store_id varchar(8) NOT NULL,
#     check_time datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
#     PRIMARY KEY (sku, store, store_id)
# );
class Inventory(models.Model):
    sku = models.CharField(max_length=15)
    quantity = models.IntegerField()
    store = models.CharField(max_length=3)
    store_id = models.CharField(max_length=8)
    check_time = models.DateTimeField(default=datetime.utcnow)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["sku", "store", "store_id"],
                name="unique_sku_store_storeID"
            )
        ]


# Create directly in MySQL
# CREATE TABLE zipcode_stores_mapping
# (
#     store char(3) NOT NULL,
#     zipcode char(5) NOT NULL,
#     store_id varchar(8) NOT NULL,
#     PRIMARY KEY (store, zipcode, store_id)
# );
class ZipcodeStoresMapping(models.Model):
    store = models.CharField(max_length=3)
    zipcode = models.CharField(max_length=5)
    store_id = models.CharField(max_length=8)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["store", "zipcode", "store_id"],
                name="unique_store_zipcode_storeID"
            )
        ]


# Create directly in MySQL
# MySQL uses POINT(lat, long)
# GeoJSON uses "coordinates": [long, lat]
# CREATE TABLE stores
# (
#     store char(3) NOT NULL,
#     store_id varchar(8) NOT NULL,
#     store_name varchar(48) NOT NULL,
#     address varchar(96) NOT NULL,
#     city varchar(24) NOT NULL,
#     state varchar(24) NOT NULL,
#     zipcode char(5) NOT NULL,
#     location POINT NOT NULL SRID 4326,
#     PRIMARY KEY (store, store_id)
# );
class Stores(models.Model):
    store = models.CharField(max_length=3)
    store_id = models.CharField(max_length=8)
    store_name = models.CharField(max_length=48)
    address = models.CharField(max_length=96)
    city = models.CharField(max_length=24)
    state = models.CharField(max_length=24)
    zipcode = models.CharField(max_length=5)
    location = PointField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["store", "store_id"],
                name="unique_store_storeID"
            )
        ]
