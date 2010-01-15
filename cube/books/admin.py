# Copyright (C) 2010  Trinity Western University

from cube.books.models import MetaBook, Book, Course, Log
from django.contrib import admin

admin.site.register(MetaBook)
admin.site.register(Book)
admin.site.register(Course)
admin.site.register(Log)
