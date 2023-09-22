from django.template.loader import get_template


def jinja_template_get_source(jinja_template):
    jinja_template_file = open(jinja_template.template.filename, "r", encoding="UTF-8")
    jinja_template_source = jinja_template_file.read()
    jinja_template_file.close()
    return jinja_template_source


def dtl_template_get_source(dtl_template):
    return dtl_template.template.source


def test_include_from_dtl_renders_jinja_inside_a_django_template():
    # no good way to create new template content at test run-time, far as I can tell,
    # so the necessary templates for this test are on disk, outside of this test file.
    # Asserting assumptions about these templates as part of this test, to make that
    # less risky

    including_jinja_name = "test_include_from_dtl__including_jinja_basic.jinja2"
    expected_jinja_content = "some jinja content"

    included_dtl_name = "test_include_from_dtl__included_dtl_basic.html"
    expected_dtl_content = "some dtl content"

    including_jinja_template = get_template(including_jinja_name)
    including_jinja_source = jinja_template_get_source(including_jinja_template)
    assert expected_jinja_content in including_jinja_source
    assert expected_dtl_content not in including_jinja_source
    assert (
        f'{{{{ include_from_dtl("{included_dtl_name}") }}}}' in including_jinja_source
    )

    included_dtl_source = dtl_template_get_source(get_template(included_dtl_name))
    assert expected_jinja_content not in included_dtl_source
    assert expected_dtl_content in included_dtl_source

    rendered_jinja_template = including_jinja_template.render({})
    assert expected_jinja_content in rendered_jinja_template
    assert expected_dtl_content in rendered_jinja_template


def test_include_from_dtl_passes_context_to_the_rendered_jinja():
    including_jinja_name = (
        "test_include_from_dtl__including_jinja_context_consuming.jinja2"
    )

    included_dtl_name = "test_include_from_dtl__included_dtl_context_consuming.html"

    context_key = "passed_context"
    context_value = "rendered value passed in context"

    including_jinja_template = get_template(including_jinja_name)
    including_jinja_source = jinja_template_get_source(including_jinja_template)
    assert context_key not in including_jinja_source
    assert context_value not in including_jinja_source

    included_dtl_source = dtl_template_get_source(get_template(included_dtl_name))
    assert context_key in included_dtl_source
    assert context_value not in included_dtl_source

    rendered_jinja_template = including_jinja_template.render(
        {context_key: context_value}
    )
    assert context_key not in rendered_jinja_template
    assert context_value in rendered_jinja_template
