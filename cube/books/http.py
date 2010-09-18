from django.http import HttpResponse

class HttpResponseNotAllowed(HttpResponse):
    status_code = 405

    def __init__(self, content, permitted_methods):
        HttpResponse.__init__(self, content=content)
        self['Allow'] = ', '.join(permitted_methods)
