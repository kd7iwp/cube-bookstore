from cube.books.models import Listing
from django.contrib import admin
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

admin.autodiscover()

list_args = {
    'queryset' : Listing.objects.all(),
}

urlpatterns = patterns('',
    (r'^$', 'cube.twupass.views.login_cube'),
    (r'^logout/', 'cube.twupass.views.logout_cube'),
    url(r'^books/', 'cube.books.views.listings', name="list"),
    #url(r'^$', 'cube.books.views.limited_object_list', list_args, name="list"),
    url(r'^help/', direct_to_template, {'template' : 'help.html'}, name="help"),
    url(r'^myBooks/', 'cube.books.views.myBooksies', name="myBooks"),
    # url(r'^myBooks/', direct_to_template, {'template' : 'myBooks.html'}, name="myBooks"),

    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/(.*)', admin.site.root),
)
