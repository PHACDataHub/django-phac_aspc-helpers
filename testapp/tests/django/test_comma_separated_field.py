from django.db import connection
from django.forms.models import ModelForm

from testapp.models import Tag, TAG_CATEGORIES


def test_csv_field_on_create():
    tag = Tag.objects.create(
        tag_categories=["fiction", "biography"],
        tag_categories_text=["fiction", "history"],
    )
    assert tag.tag_categories == ("fiction", "biography")
    assert tag.tag_categories_text == ("fiction", "history")
    assert Tag.objects.filter(
        tag_categories="fiction,biography", tag_categories_text="fiction,history"
    ).exists()


def test_csv_char_field():
    tag = Tag.objects.create()

    assert tag.tag_categories == tuple()
    tag.tag_categories = [
        "fiction",
        "history",
    ]
    tag.save()

    tag.refresh_from_db()
    assert tag.tag_categories == (
        "fiction",
        "history",
    )
    assert Tag.objects.filter(tag_categories="fiction,history").exists()

    # test forms work too
    class SystemOverviewForm(ModelForm):
        class Meta:
            model = Tag
            fields = ["tag_categories"]

    read_form = SystemOverviewForm(instance=tag)
    assert read_form.initial["tag_categories"] == (
        "fiction",
        "history",
    )
    assert read_form.fields["tag_categories"].choices[0][0] == "fiction"

    bad_form = SystemOverviewForm(
        instance=tag,
        data={
            "tag_categories": [
                "fiction",
                "bad_option",
            ]
        },
    )
    assert not bad_form.is_valid()

    write_form = SystemOverviewForm(
        instance=tag,
        data={
            "tag_categories": [
                "fiction",
                "history",
            ]
        },
    )
    assert write_form.is_valid()
    write_form.save()

    tag.refresh_from_db()
    assert tag.tag_categories == (
        "fiction",
        "history",
    )

    # now check the raw DB value is "" if we set it to []
    tag.tag_categories = []
    tag.save()

    # perform a raw query
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT tag_categories FROM testapp_tag WHERE id= {tag.id}")
        row = cursor.fetchone()

    assert row == ("",)


def test_csv_text_field():
    tag = Tag.objects.create()

    assert tag.tag_categories_text == tuple()
    tag.tag_categories_text = [
        "fiction",
        "history",
    ]
    tag.save()

    tag.refresh_from_db()
    assert tag.tag_categories_text == (
        "fiction",
        "history",
    )
    assert Tag.objects.filter(tag_categories_text="fiction,history").exists()

    # test forms work too
    class SystemOverviewForm(ModelForm):
        class Meta:
            model = Tag
            fields = ["tag_categories_text"]

    read_form = SystemOverviewForm(instance=tag)
    assert read_form.initial["tag_categories_text"] == (
        "fiction",
        "history",
    )
    assert read_form.fields["tag_categories_text"].choices[0][0] == "fiction"

    bad_form = SystemOverviewForm(
        instance=tag,
        data={
            "tag_categories_text": [
                "fiction",
                "bad_option",
            ]
        },
    )
    assert not bad_form.is_valid()

    write_form = SystemOverviewForm(
        instance=tag,
        data={
            "tag_categories_text": [
                "fiction",
                "history",
            ]
        },
    )
    assert write_form.is_valid()
    write_form.save()

    tag.refresh_from_db()
    assert tag.tag_categories_text == (
        "fiction",
        "history",
    )

    # now check the raw DB value is "" if we set it to []
    tag.tag_categories_text = tuple()
    tag.save()

    # perform a raw query
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT tag_categories_text FROM testapp_tag WHERE id= {tag.id}"
        )
        row = cursor.fetchone()

    assert row == ("",)
