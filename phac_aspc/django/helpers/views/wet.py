"""Views related to WET"""
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseNotFound

@csrf_exempt
def session(request):
    """Session refresh handler
    If the request is authenticated then the session is extended and the text
    "true" is returned, otherwise "false" is returned.
    """
    if request.method == 'PUT':
        if request.user.is_authenticated:
            request.session.modified = True
            return HttpResponse("true")

        return HttpResponse("false")

    return HttpResponseNotFound()
