from django.template.loader import get_template


def test_phac_aspc_jinja_include_renders_jinja_inside_a_django_template():
    included_jinja_template = get_template(
        "test_phac_aspc_jinja_include/included_template.jinja2"
    )

    with open(
        included_jinja_template.template.filename, "r", encoding="UTF-8"
    ) as jinja_template_file:
        jinja_template_string = jinja_template_file.read()

        assert "This is jinja" in jinja_template_string

    including_django_template = get_template(
        "test_phac_aspc_jinja_include/including_template.html"
    )

    assert "This is jinja" not in including_django_template.template.source
    assert (
        '{% phac_aspc_jinja_include "test_phac_aspc_jinja_include/included_template.jinja2" %}'
        in including_django_template.template.source
    )

    rendered_django_template = including_django_template.render({})

    assert "This is jinja" in rendered_django_template
