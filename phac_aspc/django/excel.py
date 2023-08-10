import re

from django.core.paginator import Paginator
from django.utils.functional import Promise
from django.utils.safestring import SafeString

try:
    from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
    from openpyxl.utils import escape as escapeSvc
except (ImportError, ModuleNotFoundError) as e:
    raise ImportError("must install openpyxl==3.0.10 to use excel helpers")

# Note that OPENPXYL starts columns and rows at index 1.

GLOBAL_MAX_COL_LEN = 5000


def escape_for_xlsx(text):
    return escapeSvc.escape(text) if type(text) == str else text


def create_field_val_getter(field_name):
    return lambda record: record.serializable_value(field_name)


def write_queryset_to_sheet(workbook, queryset):
    """
    iterates over queryset and puts all fields the workbook in a sheet
    - picks scalars and FK-IDs based on model
    - picks sheet name based on model
    - warning: uses queryset.iterator, prefetches are ignored
    """

    model = queryset.model
    ModelToSheetWriter(workbook=workbook, queryset=queryset).write()


def page_queryset(queryset, per_page=1000):
    """
    While in a perfect world you would use queryset.iterator(), but there is an issue that it fails to
    load any prefetch_related() fields specified. Using Paginator() we can mimic the same functionality

    > Note that if you use iterator() to run the query, prefetch_related() calls will be ignored since these two
    > optimizations do not make sense together.

    https://github.com/django-import-export/django-import-export/issues/774#issuecomment-449064652
    """

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
    def get_header():
        raise NotImplementedError()

    def get_value(self, record):
        raise NotImplementedError()

    def serialize_value(self, value):
        return serialize_value(value)

    def get_serialized_value(self, record):
        return self.serialize_value(self.get_value(record))


class ModelColumn(Column):
    def __init__(self, model_cls, field_name, header_value=None):
        self.header_value = header_value
        self.model_cls = model_cls
        self.field_name = field_name
        self.get_val = create_field_val_getter(field_name)

    def get_header(self):
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


class ModelToSheetWriter:
    def __init__(self, workbook, queryset):
        self.workbook = workbook
        self.queryset = queryset
        self.model = queryset.model

    def get_column_configs(self):
        fields_to_write = self.model._meta.fields
        return [
            ModelColumn(self.model, field.name) for field in fields_to_write
        ]

    def get_sheet_name(self):
        return get_default_sheet_name_for_qs(self.queryset)

    def get_header_row(self):
        # return [escape_for_xlsx(name) for name, _ in self.get_column_configs()]
        return [
            serialize_value(col.get_header())
            for col in self.get_column_configs()
        ]

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
    model_name = queryset.model._meta.verbose_name
    return f"{model_name[:30]}"


