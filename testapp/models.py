from django.conf import settings
from django.db import models
from django.utils import timezone

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass


class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)


class Tag(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class Book(models.Model):
    # changelog_live_name_loader_class = BookNameLoader

    author = models.ForeignKey(Author, related_name="books", on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    tags = models.ManyToManyField(Tag)
