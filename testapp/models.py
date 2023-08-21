from django.conf import settings
from django.db import models
from django.utils import timezone

from phac_aspc.django import fields

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass


class Author(models.Model):
    first_name = fields.CharField(max_length=100)
    last_name = fields.CharField(max_length=100)


class Tag(models.Model):
    name = fields.CharField(max_length=250)

    def __str__(self):
        return self.name


class Book(models.Model):
    # changelog_live_name_loader_class = BookNameLoader

    author = fields.ForeignKey(Author, related_name="books", on_delete=models.CASCADE)
    title = fields.CharField(max_length=250)
    tags = fields.ManyToManyField(Tag)
