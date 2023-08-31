from phac_aspc.django.excel import (
    ModelToSheetWriter,
    ModelColumn,
    CustomColumn,
    ManyToManyColumn,
    AbstractExportView,
)
from django.test import RequestFactory
import random

from openpyxl import Workbook
from testapp.models import Book
from testapp.model_factories import TagFactory, BookFactory


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
