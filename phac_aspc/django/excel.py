# pylint: disable=missing-function-docstring, missing-class-docstring
"""
utilities for writing excel data using openpyxl 
"""
import re

from django.core.paginator import Paginator
from django.views import View
from django.http import HttpResponse
from django.utils.functional import Promise
from django.utils.safestring import SafeString

try:
    import openpyxl
    from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
    from openpyxl.utils import escape as escapeSvc
except (ImportError, ModuleNotFoundError) as exc:
    raise ImportError("must install openpyxl==3.0.10 to use excel helpers") from exc

# Note that OPENPXYL starts columns and rows at index 1.


GLOBAL_MAX_COL_LEN = 5000


def escape_for_xlsx(text):
    """
    escape a string for excel
    """
    # pylint: disable=unidiomatic-typecheck
    return escapeSvc.escape(text) if type(text) == str else text


def create_field_val_getter(field_name):
    """
    returns a function that gets the value of a field for a django model instance
    """
    return lambda record: record.serializable_value(field_name)


def write_queryset_to_sheet(workbook, queryset):
    """
    iterates over queryset and puts all fields the workbook in a sheet
    - picks scalars and FK-IDs based on model
    - picks sheet name based on model
    - warning: uses queryset.iterator, prefetches are ignored
    """

    ModelToSheetWriter(workbook=workbook, queryset=queryset).write()


def page_queryset(queryset, per_page=1000):
    """
    While in a perfect world you would use queryset.iterator()
    but there is an issue that it fails to
    load any prefetch_related() fields specified.
    Paginator() can mimic the same functionality

    https://github.com/django-import-export/django-import-export/issues/774#issuecomment-449064652
    """

    # pylint: disable=protected-access
    if queryset._prefetch_related_lookups:
        if not queryset.query.order_by:
            # Paginator() throws a warning if there is no sorting attached to the queryset
            queryset = queryset.order_by("pk")
        paginator = Paginator(queryset, per_page)
        for index in range(paginator.num_pages):
            yield from paginator.get_page(index + 1)
    else:
        yield from queryset.iterator(chunk_size=per_page)


class Column:
    """
    Base class to write columns in a sheet
    """

    def get_header(self):
        """return a header string for the column"""
        raise NotImplementedError()

    def get_value(self, record):
        """return this column's intended cell value for a record"""
        raise NotImplementedError()

    def serialize_value(self, value):
        return serialize_value(value)

    def get_serialized_value(self, record):
        return self.serialize_value(self.get_value(record))


class ModelColumn(Column):
    """
    shorthand for defining a column that writes a scalar model field (non foreign-key)
    """

    def __init__(self, model_cls, field_name, header_value=None):
        self.header_value = header_value
        self.model_cls = model_cls
        self.field_name = field_name
        self.get_val = create_field_val_getter(field_name)

    def get_header(self):
        # pylint: disable=protected-access
        header_value = (
            self.header_value
            or self.model_cls._meta.get_field(self.field_name).verbose_name
        )
        return escape_for_xlsx(header_value)

    def get_value(self, record):
        return self.get_val(record)


class ChoiceColumn(Column):
    def __init__(self, model_cls, field_name, header_value=None):
        self.header_value = header_value
        self.model_cls = model_cls
        self.field_name = field_name

    def get_header(self):
        # pylint: disable=protected-access
        header_value = (
            self.header_value
            or self.model_cls._meta.get_field(self.field_name).verbose_name
        )
        return escape_for_xlsx(header_value)

    def get_value(self, record):
        method_name = "get_" + self.field_name + "_display"
        return getattr(record, method_name)()


class CustomColumn(Column):
    def __init__(self, header, get_val):
        self.header = header
        self.get_val = get_val

    def get_header(self):
        return self.header

    def get_value(self, record):
        return self.get_val(record)


class ManyToManyColumn(Column):
    # pylint: disable=too-many-arguments
    def __init__(
        self,
        model: type,
        field_name: str,
        get_related_str: callable = None,
        delimiter: str = ", ",
        header=None,
    ):
        self.model = model
        self.field_name = field_name
        self.header = header
        if get_related_str:
            self.get_related_str = get_related_str
        else:
            self.get_related_str = lambda x, *args: str(x)

        self.delimiter = delimiter

    def get_header(self):
        if self.header:
            return self.header
        # pylint: disable=protected-access
        return self.model._meta.get_field(self.field_name).verbose_name

    def get_value(self, record):
        related_records = list(getattr(record, self.field_name).all())
        return self.delimiter.join([self.get_related_str(x) for x in related_records])


class ModelToSheetWriter:
    def __init__(self, workbook, queryset):
        self.workbook = workbook
        self.queryset = queryset
        self.model = queryset.model

    def get_column_configs(self):
        # pylint: disable=protected-access
        fields_to_write = self.model._meta.fields
        return [ModelColumn(self.model, field.name) for field in fields_to_write]

    def get_sheet_name(self):
        return get_default_sheet_name_for_qs(self.queryset)

    def get_header_row(self):
        # return [escape_for_xlsx(name) for name, _ in self.get_column_configs()]
        return [serialize_value(col.get_header()) for col in self.get_column_configs()]

    def write(self):
        worksheet = self.workbook.create_sheet(title=self.get_sheet_name())

        worksheet.append(self.get_header_row())

        iterator = page_queryset(self.queryset)
        for record in iterator:
            xl_row = []
            for col in self.get_column_configs():
                xl_val = col.get_serialized_value(record)
                xl_row.append(xl_val)

            worksheet.append(xl_row)


def serialize_value(value):
    if value is None:
        write_val = ""
    else:
        if value is True:
            write_val = 1
        elif value is False:
            write_val = 0
        elif isinstance(value, list):
            write_val = str(value)
        elif isinstance(value, (Promise, SafeString)):
            # tm values don't play well with excel
            write_val = value + ""
        else:
            write_val = value

    xl_val = escape_for_xlsx(write_val)
    if next(ILLEGAL_CHARACTERS_RE.finditer(str(value)), None):
        xl_val = re.sub(ILLEGAL_CHARACTERS_RE, "", str(xl_val))

    return xl_val


def get_manager_for_export(model):
    return getattr(model, "no_fakes", model.objects)


def get_default_sheet_name_for_qs(queryset):
    """
    excel only supports up to 31 characters in a worksheet name
    """
    # pylint: disable=protected-access
    model_name = queryset.model._meta.verbose_name
    return f"{model_name[:30]}"


class AbstractExportView(View):
    def get_filename(self):
        return "export.xlsx"

    def get_queryset(self):
        try:
            return self.queryset
        except AttributeError as e:
            raise NotImplementedError(
                "Must define queryset attr or override get_queryset()"
            ) from e

    def get_sheetwriter_class(self):
        try:
            return self.sheetwriter_class
        except AttributeError as e:
            raise NotImplementedError(
                "Must define sheetwriter_class attr or override get_sheetwriter_class()"
            ) from e

    def get(self, request, *args, **kwargs):
        wb = openpyxl.Workbook(write_only=True)
        WriterCls = self.get_sheetwriter_class()
        writer = WriterCls(
            workbook=wb,
            queryset=self.get_queryset(),
        )
        writer.write()
        response = HttpResponse(headers={"Content-Type": "application/vnd.ms-excel"})
        response["Content-Disposition"] = f"attachment; filename={self.get_filename()}"
        wb.save(response)
        return response
