# Safe Edit Tests

There are no automated tests for this component, however to test the various
functionality provided by the macro, add the following lines to the bottom of
your urls.py temporarily:

```python

from core.utils import get_html
urlpatterns += (
    path('test_safe_edits', lambda request: get_html(request, "macros/tests/page.jinja2", {}), name='test_safe_edits'),
    path('test_safe_edits_call_form', lambda request: get_html(request, "macros/tests/call_form.jinja2", {}), name='test_safe_edits_call_form'),
    path('test_safe_edits_form', lambda request: get_html(request, "macros/tests/form.jinja2", {}), name='test_safe_edits_form'),
)

```

Visit http://localhost:8000/test_safe_edits to view the playground.
