# Copyright (C) 2010  Trinity Western University

from cube.books.models import Book
from django.contrib.auth.models import User

from django.contrib import admin
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'cube.twupass.views.login_cube'),
    (r'^logout/$', 'cube.twupass.views.logout_cube'),

    url(r'^books/$', 'cube.books.views.books.book_list', name="list"),
    url(r'^books/update/book/$', 'cube.books.views.books.update_book',
        name="update_book"),
    url(r'^books/update/book/edit/$', 'cube.books.views.books.update_book_edit',
        name="update_book_edit"),

    # metabooks
    url(r'^metabooks/$','cube.books.views.metabooks.metabook_list', name="list_metabooks"),
    url(r'metabooks/update/$', 'cube.books.views.metabooks.update',
        name="update_metabooks"),

    url(r'^add_book/$', 'cube.books.views.books.add_book', name="add_book"),
    url(r'^add_new_book/$', 'cube.books.views.books.add_new_book',
        name="add_new_book"),
    url(r'^attach_book/$', 'cube.books.views.books.attach_book', name="attach_book"),
    url(r'^help/$', direct_to_template, {'template' : 'help.html'}, name="help"),
    url(r'^my_books/$', 'cube.books.views.books.my_books', name="my_books"),
    url(r'^staff/$','cube.books.views.staff.staff_list', name="staff"),
    url(r'^staff_edit/$','cube.books.views.staff.staff_edit', name="staff_edit"),
    url(r'^update_staff/$','cube.books.views.staff.update_staff', name="update_staff"),

    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/(.*)', admin.site.root),

    # TODO remove this for live server
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': 'C:/Documents and Settings/OEM User/My Documents/cube-bookstore/media/'}),
    
)
