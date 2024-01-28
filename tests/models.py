from django.db import models


class User(models.Model):
    name = models.CharField(max_length=30)
    email = models.EmailField()
    join_date = models.DateField()
    last_active = models.DateTimeField()


class Country(models.Model):
    name = models.CharField(max_length=30)
