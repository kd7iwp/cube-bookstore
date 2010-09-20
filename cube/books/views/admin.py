from cube.books.models import Book, Log, MetaBook

from django.db.models import get_models, get_app
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden, HttpResponse
from django.shortcuts import render_to_response as rtr
from django.template import loader, RequestContext as RC

@login_required()
def dumpdata(request):
    """
    Written so that you don't have to have shell access
    to get a fixture from the website

    Tests:
        - GETTest
        - SecurityTest
    """
    # TODO bad method of identifying the superuser. Start using django's groups
    if not request.user == User.objects.get(pk=1):
        t = loader.get_template('403.html')
        c = RC(request)
        return HttpResponseForbidden(t.render(c))
    app_labels = ['auth', 'books']
    apps = map(get_app, app_labels)
    models = []
    for app in apps: models.extend(get_models(app))
    objects = []
    for model in models:
        if not model._meta.proxy: objects.extend(model._default_manager.all())
    serialized = serializers.serialize('json', objects, indent=True)
    return HttpResponse(serialized, mimetype="application/json")

@login_required()
def bad_unholds(request):
    """
    Tests:
        - GETTest
        - SecurityTest
    """
    # TODO bad method of identifying the superuser. Start using django's groups
    if not request.user == User.objects.get(pk=1):
        t = loader.get_template('403.html')
        c = RC(request, {})
        return HttpResponseForbidden(t.render(c))
    entries = []
    for book in Book.objects.all():
        logs = Log.objects.filter(book=book) 
        for r_log in logs.filter(action='R'):
            bad_actions = ['M', 'P', 'S', 'T', 'D']
            bad_logs = logs.filter(action__in=bad_actions, when__lte=r_log.when)
            if bad_logs.count() > 0:
                # If a book has been marked as Missing, On Hold, Sold
                # To Be Deleted of Deleted before having a hold removed
                entry = []
                for log in logs: entry.append((log, True if log == r_log else False))
                entries.append(entry)
    var_dict = {
        'entries' : entries,
    }
    return rtr('books/admin/bad_unholds.html', var_dict, context_instance=RC(request)) 

def get_orphandupe_metabooks():
    """
    Returns all metabooks which have duplicate barcodes and which are not
    attached to any book
    """
    dupes = []
    for metabook in MetaBook.objects.all():
        if MetaBook.objects.filter(barcode=metabook.barcode).count() > 1 and\
           Book.objects.filter(metabook=metabook).count() == 0:
            dupes.append(metabook)
    return dupes

@login_required()
def duplicate_metabooks(request):
    # TODO bad method of identifying the superuser. Start using django's groups
    if not request.user == User.objects.get(pk=1):
        t = loader.get_template('403.html')
        c = RC(request, {})
        return HttpResponseForbidden(t.render(c))
    var_dict = {
        'dupes' : get_orphandupe_metabooks(),
    }
    return rtr('books/admin/duplicate_metabooks.html', var_dict,
                context_instance=RC(request))
@login_required()
def delete_duplicate_metabooks(request):
    # TODO bad method of identifying the superuser. Start using django's groups
    if not request.user == User.objects.get(pk=1):
        t = loader.get_template('403.html')
        c = RC(request, {})
        return HttpResponseForbidden(t.render(c))
    for dupe in get_orphandupe_metabooks():
        dupe.delete()
    return HttpResponse('Deleted')
