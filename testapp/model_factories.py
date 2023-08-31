import factory

from .models import Book, Author, Tag


class AuthorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Author

    first_name = factory.Faker("bs")
    last_name = factory.Faker("bs")


class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tag

    name = factory.Faker("bs")


class BookFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Book

    author = factory.SubFactory(AuthorFactory)
    title = factory.Faker("bs")
