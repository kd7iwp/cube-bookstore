from django.db.models import get_models, get_app
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden, HttpResponse
from django.shortcuts import render_to_response as rtr
from django.template import RequestContext as RC

@login_required
def dumpdata(request):
    """
    Written so that you don't have to have shell access
    to get a fixture from the website
    """
    # TODO bad method of identifying the superuser. Start using django's groups
    #TODO write tests
    if not request.user == User.objects.get(pk=1):
        return HttpResponseForbidden()
    app_labels = ['auth', 'books']
    apps = map(get_app, app_labels)
    models = []
    for app in apps: models.extend(get_models(app))
    objects = []
    for model in models:
        if not model._meta.proxy: objects.extend(model._default_manager.all())
    serialized = serializers.serialize('json', objects, indent=True)
    return HttpResponse(serialized, mimetype="application/json")
