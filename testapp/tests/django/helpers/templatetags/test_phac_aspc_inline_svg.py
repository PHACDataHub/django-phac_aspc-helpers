import os
import re

from django.template import Context, Template

test_svg_name = "test_phac_aspc_inline_svg.svg"


def test_phac_aspc_inline_svg_inlines_svg_content_from_file():
    with open(
        os.path.join(os.path.dirname(__file__), "static", test_svg_name),
        "r",
        encoding="UTF-8",
    ) as svg_file:
        svg_file_content = svg_file.read()

        template_with_inlined_svg = Template(
            "{% load phac_aspc_inline_svg %}\n"
            + f"{{% phac_aspc_inline_svg '{test_svg_name}' %}}"
        ).render(Context({}))

        assert svg_file_content.strip() == template_with_inlined_svg.strip()


def test_phac_aspc_inline_svg_sets_provided_attributes():
    svg_name = "test_phac_aspc_inline_svg.svg"

    attribute1 = "width"
    value1 = "2rem"

    attribute2 = "class"
    value2 = "some-class"

    template_with_inlined_svg = Template(
        "{% load phac_aspc_inline_svg %}\n"
        + f"{{% phac_aspc_inline_svg '{svg_name}' "
        + f"{attribute1}='{value1}' {attribute2}='{value2}' %}}"
    ).render(Context({}))

    for attribute, value in [[attribute1, value1], [attribute2, value2]]:
        assert (
            len(
                re.findall(
                    f"<svg .*{attribute}=['\"]{value}['\"].*>",
                    template_with_inlined_svg,
                )
            )
            == 1
        )
