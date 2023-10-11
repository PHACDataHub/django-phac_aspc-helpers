import io
from phac_aspc.django.excel import (
    ModelToSheetWriter,
    ModelColumn,
    CustomColumn,
    ManyToManyColumn,
    AbstractExportView,
    ModelToCsvWriter,
    AbstractCsvExportView,
)
from django.test import RequestFactory
import random

from openpyxl import Workbook
from testapp.models import Book
from testapp.model_factories import TagFactory, BookFactory, AuthorFactory


def create_data():
    all_tags = [TagFactory() for _ in range(6)]

    for _ in range(30):
        book = BookFactory()
        tags = random.sample(all_tags, random.randint(0, 4))
        book.tags.set(tags)


def test_model_to_sheet_writer(django_assert_max_num_queries):
    create_data()

    columns = [
        ModelColumn(Book, "title"),
        CustomColumn("Author", lambda x: f"{x.author.first_name} {x.author.last_name}"),
        ManyToManyColumn(Book, "tags"),
    ]

    class BookSheetWriter(ModelToSheetWriter):
        model = Book

        def get_column_configs(self):
            return columns

    with django_assert_max_num_queries(4):
        wb = Workbook()
        writer = BookSheetWriter(
            workbook=wb, queryset=Book.objects.all().prefetch_related("author", "tags")
        )
        writer.write()


def test_abstract_view():
    create_data()

    class BookSheetWriter(ModelToSheetWriter):
        model = Book

        def get_column_configs(self):
            return [
                ModelColumn(Book, "title"),
                CustomColumn(
                    "Author", lambda x: f"{x.author.first_name} {x.author.last_name}"
                ),
                ManyToManyColumn(Book, "tags"),
            ]

    class BookExportView(AbstractExportView):
        sheetwriter_class = BookSheetWriter
        queryset = Book.objects.all().prefetch_related("author", "tags")

    view_func = BookExportView.as_view()
    req_factory = RequestFactory()
    request = req_factory.get("/fake-url")

    response = view_func(request)
    assert response.status_code == 200


def test_csv_writer():
    class BookCsvWriter(ModelToCsvWriter):
        model = Book

        def get_column_configs(self):
            return [
                ModelColumn(Book, "title"),
                CustomColumn(
                    "Author", lambda x: f"{x.author.first_name} {x.author.last_name}"
                ),
                ManyToManyColumn(Book, "tags", delimiter="|"),
            ]

    # test view response
    class BookExportView(AbstractCsvExportView):
        writer_class = BookCsvWriter
        queryset = Book.objects.all().prefetch_related("author", "tags")

    t1 = TagFactory(name="t1")
    t2 = TagFactory(name="t2")
    a1 = AuthorFactory(first_name="bôb", last_name="l'ébob")
    b1 = BookFactory(title="b1", author=a1)
    b1.tags.set([t1, t2])
    b2 = BookFactory(title="b2 çûèêëcks", author=a1)

    view_func = BookExportView.as_view()
    req_factory = RequestFactory()
    request = req_factory.get("/fake-url", headers={"Accept": "text/csv"})
    response = view_func(request)
    assert response.status_code == 200

    # test serialization
    # TODO: figure out why testing response content directly fails
    # for some reason it escapes utf8
    file = io.StringIO()
    writer = BookCsvWriter(file, Book.objects.filter(id__in=[b1.id, b2.id]))
    writer.write()
    as_str = file.getvalue()
    assert (
        as_str
        == "title,Author,tags\r\nb1,bôb l'ébob,t1|t2\r\nb2 çûèêëcks,bôb l'ébob,\r\n"
    )
