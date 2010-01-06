from cube.books.models import Listing
from django.contrib.auth.models import User

from django.contrib import admin
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'cube.twupass.views.login_cube'),
    (r'^logout/$', 'cube.twupass.views.logout_cube'),

    url(r'^books/$', 'cube.books.views.listings', name="list"),
    url(r'^books/update/$', 'cube.books.views.update_data', name="update_data"),
    url(r'^books/update/listing/$', 'cube.books.views.update_listing',
        name="update_listing"),
    url(r'books/update/book/$', 'cube.books.views.update_books',
        name="update_books"),

    url(r'^addBooks/$', 'cube.books.views.addBooks', name="addBooks"),
    url(r'^help/$', direct_to_template, {'template' : 'help.html'}, name="help"),
    url(r'^myBooks/$', 'cube.books.views.myBooksies', name="myBooks"),
    url(r'^staff/$','cube.books.views.staff', name="staff"),
    url(r'^staffedit/$','cube.books.views.staffedit', name="staffedit"),
    url(r'^update_staff/$','cube.books.views.update_staff', name="update_staff"),
    url(r'^listBooks/$','cube.books.views.listBooks', name="listBooks"),

    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/(.*)', admin.site.root),

    # TODO remove this for live server
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': 'C:/Documents and Settings/david.somers-harris/Desktop/code/cube-bookstore/media'}),
    
)
