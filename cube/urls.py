from cube.books.models import Listing
from django.contrib import admin
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.views.generic.list_detail import object_list

admin.autodiscover()

list_args = {
    'queryset' : Listing.objects.all(),
}
# TODO add paginate_by : 30

urlpatterns = patterns('',
    url(r'^$', object_list, list_args, name="list"),
    url(r'^help/', direct_to_template, {'template' : 'help.html'}, name="help"),
    url(r'^myBooks/', 'cube.books.views.myBooksies', name="myBooks"),
    # url(r'^myBooks/', direct_to_template, {'template' : 'myBooks.html'}, name="myBooks"),

    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/(.*)', admin.site.root),
)
