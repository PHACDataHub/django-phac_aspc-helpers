from django.urls import include, path, re_path


def view_for_template(template_name):
    def view_func(request):
        from django.shortcuts import render

        return render(request, template_name)

    return view_func


urlpatterns = [
    path(
        "with_language_tag/",
        view_for_template("language_tag_example.jinja2"),
        name="with_language_tag",
    ),
]
