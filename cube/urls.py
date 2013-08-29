# Copyright (C) 2010  Trinity Western University

from cube.books.models import Book
from cube.twupass.settings import TWUPASS_LOGOUT_URL
from django.contrib.auth.models import User

from django.contrib import admin
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template, redirect_to

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^twupass-logout/$', redirect_to, {'url': TWUPASS_LOGOUT_URL},
        name="twupass-logout"),
    url(r'^help/$', direct_to_template, {'template' : 'help.html'},
        name="help"),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/(.*)', admin.site.root),
)

urlpatterns += patterns('cube.twupass.views',
    (r'^$', 'login_cube'),
    (r'^logout/$', 'logout_cube')
)

urlpatterns += patterns('cube.books.views.books',
    url(r'^books/$', 'book_list', name="list"),
    url(r'^books/update/book/$', 'update_book', name="update_book"),
    url(r'^books/update/book/edit/$', 'update_book_edit', 
            name="update_book_edit"),
    url(r'books/update/remove_holds_by_user/$', 'remove_holds_by_user', 
            name="remove_holds_by_user"),
    url(r'^add_book/$', 'add_book', name="add_book"),
    url(r'^add_new_book/$', 'add_new_book', name="add_new_book"),
    url(r'^attach_book/$', 'attach_book', name="attach_book"),
    url(r'^my_books/$', 'my_books', name="my_books"),
)

urlpatterns += patterns('cube.books.views.reports',
    url(r'^reports/$', 'menu', name="reports_menu"),
    url(r'^reports/per_status/$', 'per_status', name='per_status'),
    url(r'^reports/books_sold_within_date/$', 'books_sold_within_date',
        name='books_sold_within_date'),
    url(r'^reports/user/(\d+)/$', 'user', name='user'),
    url(r'^reports/book/(\d+)/$', 'book', name='book'),
    url(r'^reports/metabook/(\d+)/$', 'metabook', name='metabook'),
    url(r'^reports/holds_by_user/$', 'holds_by_user', name='holds_by_user'),
)

urlpatterns += patterns('cube.books.views.metabooks',
    url(r'^metabooks/$','metabook_list', name="list_metabooks"),
    url(r'metabooks/update/$', 'update', name="update_metabooks"),
)

urlpatterns += patterns('cube.books.views.staff',
    url(r'^staff/$','staff_list', name="staff"),
    url(r'^staff_edit/$','staff_edit', name="staff_edit"),
    url(r'^update_staff/$','update_staff', name="update_staff"),
)

urlpatterns += patterns('cube.books.views.admin',
    url(r'^books/admin/dumpdata/$', 'dumpdata', name='dumpdata'),
    url(r'^books/admin/bad_unholds/$', 'bad_unholds', name='bad_unholds'),
)

urlpatterns += patterns('cube.users.views',
    url(r'^profile/$', 'profile', name='profile'),
    url(r'^profile/edit/$', 'edit_profile', name='edit_profile')
)

urlpatterns += patterns('cube.settings.views',
    url(r'^settings/', 'edit_settings', name='edit_settings')
)
