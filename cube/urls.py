from cube.books.models import Listing
from django.contrib.auth.models import User

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
    url(r'^books/$', 'cube.books.views.listings', name="list"),
    url(r'^books/update', 'cube.books.views.update_data', name="update_data"),

    url(r'^my/', direct_to_template, {'template' : 'books/mybooks.html'}, name="my"),
    
    url(r'^help/', direct_to_template, {'template' : 'help.html'}, name="help"),
    url(r'^myBooks/', 'cube.books.views.myBooksies', name="myBooks"),
    url(r'^staff/','cube.books.views.staff', name="staff"),
    url(r'^staffedit/','cube.books.views.staffedit', name="staffedit"),




    # url(r'^myBooks/', direct_to_template, {'template' : 'myBooks.html'}, name="myBooks"),





    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/(.*)', admin.site.root),
)
