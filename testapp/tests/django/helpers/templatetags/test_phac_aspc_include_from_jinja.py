from django.template.loader import get_template


def jinja_template_get_source(jinja_template):
    jinja_template_file = open(
        jinja_template.template.filename, "r", encoding="UTF-8"
    )
    jinja_template_source = jinja_template_file.read()
    jinja_template_file.close()
    return jinja_template_source


def dtl_template_get_source(dtl_template):
    return dtl_template.template.source


def test_phac_aspc_include_from_jinja_renders_jinja_inside_a_django_template():
    # no good way to create new template content at test run-time, far as I can tell,
    # so the necessary templates for this test are on disk, outside of this test file.
    # Asserting assumptions about these templates as part of this test, to make that
    # less risky

    included_jinja_name = (
        "test_phac_aspc_include_from_jinja__included_jinja_basic.jinja2"
    )
    expected_jinja_content = "some jinja content"

    including_dtl_name = (
        "test_phac_aspc_include_from_jinja__including_dtl_basic.html"
    )
    expected_dtl_content = "some dtl content"

    included_jinja_source = jinja_template_get_source(
        get_template(included_jinja_name)
    )
    assert expected_jinja_content in included_jinja_source
    assert expected_dtl_content not in included_jinja_source

    including_dtl_template = get_template(including_dtl_name)
    including_dtl_source = dtl_template_get_source(including_dtl_template)
    assert expected_jinja_content not in including_dtl_source
    assert expected_dtl_content in including_dtl_source
    assert (
        f'{{% phac_aspc_include_from_jinja "{included_jinja_name}" %}}'
        in including_dtl_source
    )

    rendered_dtl_template = including_dtl_template.render({})
    assert expected_jinja_content in rendered_dtl_template
    assert expected_dtl_content in rendered_dtl_template


def test_phac_aspc_include_from_jinja_passes_context_to_the_rendered_jinja():
    included_jinja_name = "test_phac_aspc_include_from_jinja__included_jinja_context_consuming.jinja2"

    including_dtl_name = "test_phac_aspc_include_from_jinja__including_dtl_context_consuming.html"

    context_key = "passed_context"
    context_value = "rendered value passed in context"

    included_jinja_source = jinja_template_get_source(
        get_template(included_jinja_name)
    )
    assert context_key in included_jinja_source
    assert context_value not in included_jinja_source

    including_dtl_template = get_template(including_dtl_name)
    including_dtl_source = dtl_template_get_source(including_dtl_template)
    assert context_key not in including_dtl_source
    assert context_value not in including_dtl_source

    rendered_dtl_template = including_dtl_template.render(
        {context_key: context_value}
    )
    assert context_key not in rendered_dtl_template
    assert context_value in rendered_dtl_template
