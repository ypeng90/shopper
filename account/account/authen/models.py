from django.db import models

# Create directly in MySQL.
# CREATE TABLE users
# (
#     username varchar(20) NOT NULL,
#     userid int NOT NULL UNIQUE,
#     password char(64) NOT NULL,
#     salt char(64) NOT NULL,
#     PRIMARY KEY (username)
# );


# Create your models here.
class Users(models.Model):
    username = models.CharField(primary_key=True, max_length=20)
    userid = models.IntegerField(unique=True)
    password = models.CharField(max_length=64)
    salt = models.CharField(max_length=64)
