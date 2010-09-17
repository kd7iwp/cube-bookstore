# Copyright (C) 2010  Trinity Western University

from cube.books.models import Book
from cube.twupass.settings import TWUPASS_LOGOUT_URL
from django.contrib.auth.models import User

from django.contrib import admin
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template, redirect_to

admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'cube.twupass.views.login_cube'),
    (r'^logout/$', 'cube.twupass.views.logout_cube'),
    url(r'^twupass-logout/$', redirect_to, {'url': TWUPASS_LOGOUT_URL},
        name="twupass-logout"),

    url(r'^books/$', 'cube.books.views.books.book_list', name="list"),
    url(r'^books/update/book/$', 'cube.books.views.books.update_book',
        name="update_book"),
    url(r'^books/update/book/edit/$', 'cube.books.views.books.update_book_edit',
        name="update_book_edit"),
    url(r'books/update/remove_holds_by_user/$', 'cube.books.views.books.remove_holds_by_user', name="remove_holds_by_user"),
    
    # reports
    url(r'^reports/$', 'cube.books.views.reports.menu', name="reports_menu"),
    url(r'^reports/per_status/$', 'cube.books.views.reports.per_status',
        name='per_status'),
    url(r'^reports/books_sold_within_date/$', 
        'cube.books.views.reports.books_sold_within_date',
	name='books_sold_within_date'),
    url(r'^reports/user/(\d+)/$', 'cube.books.views.reports.user', name='user'),
    url(r'^reports/book/(\d+)/$', 'cube.books.views.reports.book', name='book'),
    url(r'^reports/metabook/(\d+)/$', 'cube.books.views.reports.metabook', name='metabook'),
    url(r'^reports/holds_by_user/$', 'cube.books.views.reports.holds_by_user', name='holds_by_user'),

    # metabooks
    url(r'^metabooks/$','cube.books.views.metabooks.metabook_list',
        name="list_metabooks"),
    url(r'metabooks/update/$', 'cube.books.views.metabooks.update',
        name="update_metabooks"),

    url(r'^add_book/$', 'cube.books.views.books.add_book', name="add_book"),
    url(r'^add_new_book/$', 'cube.books.views.books.add_new_book',
        name="add_new_book"),
    url(r'^attach_book/$', 'cube.books.views.books.attach_book',
        name="attach_book"),
    url(r'^help/$', direct_to_template, {'template' : 'help.html'},
        name="help"),
    url(r'^my_books/$', 'cube.books.views.books.my_books', name="my_books"),
    url(r'^staff/$','cube.books.views.staff.staff_list', name="staff"),
    url(r'^staff_edit/$','cube.books.views.staff.staff_edit',
        name="staff_edit"),
    url(r'^update_staff/$','cube.books.views.staff.update_staff',
        name="update_staff"),

    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/(.*)', admin.site.root),


    # Cube Admin
    url(r'^books/admin/dumpdata/$', 'cube.books.views.admin.dumpdata',
        name='dumpdata'),
    url(r'^books/admin/bad_unholds/$', 'cube.books.views.admin.bad_unholds',
        name='bad_unholds'),

    # TODO remove this for live server
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': '/home/david/code/cube-bookstore/media/'}),
    
)
