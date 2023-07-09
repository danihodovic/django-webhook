from django.db import models


class User(models.Model):
    name = models.CharField(max_length=30)
    email = models.EmailField()


class Country(models.Model):
    name = models.CharField(max_length=30)
