from cube.books.models import Book
from django.contrib.auth.models import User

from django.contrib import admin
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'cube.twupass.views.login_cube'),
    (r'^logout/$', 'cube.twupass.views.logout_cube'),

    url(r'^books/$', 'cube.books.views.books.books', name="list"),
    url(r'^books/update/book/$', 'cube.books.views.books.update_book',
        name="update_book"),
    url(r'^books/update/book/edit/$', 'cube.books.views.books.update_book_edit',
        name="update_book_edit"),
    url(r'books/update/metabook/$', 'cube.books.views.books.update_metabooks',
        name="update_metabooks"),

    url(r'^add_book/$', 'cube.books.views.books.add_book', name="add_book"),
    url(r'^add_new_book/$', 'cube.books.views.books.add_new_book',
        name="add_new_book"),
    url(r'^attach_book/$', 'cube.books.views.books.attach_book', name="attach_book"),
    url(r'^help/$', direct_to_template, {'template' : 'help.html'}, name="help"),
    url(r'^my_books/$', 'cube.books.views.books.my_books', name="my_books"),
    url(r'^staff/$','cube.books.views.staff.staff', name="staff"),
    url(r'^staffedit/$','cube.books.views.staff.staffedit', name="staffedit"),
    url(r'^update_staff/$','cube.books.views.staff.update_staff', name="update_staff"),
    url(r'^list_metabooks/$','cube.books.views.books.list_metabooks', name="list_metabooks"),

    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/(.*)', admin.site.root),

    # TODO remove this for live server
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': 'C:/Documents and Settings/david.somers-harris/Desktop/code/cube-bookstore/media'}),
    
)
