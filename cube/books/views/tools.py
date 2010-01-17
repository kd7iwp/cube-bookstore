# Copyright (C) 2010  Trinity Western University

from cube.books.models import Book, MetaBook
from cube.books.email import send_tbd_emails
from django.db.models.query import QuerySet
from datetime import datetime, timedelta
from django.shortcuts import render_to_response
from django.template import RequestContext

def expire_holds():
    """
    Expires holds on books after 24 hours
    """
    yester = datetime.today() - timedelta(1)
    expired_books = Book.objects.filter(status='O', hold_date__lte=yester)
    expired_books.update(status='F', holder=None, hold_date=None)

def warn_annual_sellers():
    """
    If a book is a year old, mark it as to be deleted and send them an email
    """
    last_year = datetime.today() - timedelta(365)
    old_books = Book.objects.filter(status='F', list_date__lte=last_year)
    if old_books.count():
        send_tbd_emails(old_books)
        old_books.update(status='T')

def house_cleaning():
    """
    calls methods which need to be done frequently
    """
    expire_holds()
    warn_annual_sellers()

def tidy_error(request, error_message):
    """
    takes a request and an error message and returns a
    tidy HttpResponse with it
    """
    return render_to_response('error.html', {'message' : error_message },
                              context_instance=RequestContext(request))
def get_number(list, key, default):
    """
    grabs a string from a list and converts it to a number
    if it can't, then it returns the integer conversion of default
    which is assumed to work
    """
    try:
        number = int(list.get(key, default))
    except ValueError:
        number = int(default)
    return number

def book_filter(filter, field, books):
    """
    Returns a filtered list of Book objects only if the field is valid
    otherwise it returns all of the book objects
    """
    def status(filter):
        for choice in Book.STATUS_CHOICES:
            if filter.lower() in choice[1].lower():
                return books.filter(status=choice[0])
        return Book.objects.none()

    def course(filter):
        q = books
        f = books.filter
        for word in filter.split():
            try:
                x = int(word)
                q = q & f(metabook__courses__number__icontains=word)
            except ValueError:
                q = q & f(metabook__courses__department__icontains=word)
        return q.distinct()

    def ref(filter):
        try:
            return books.filter(pk=int(filter))
        except ValueError:
            return Book.objects.none()

    def title(filter):
        return books.filter(metabook__title__icontains=filter)

    def author(filter):
        return books.filter(metabook__author__icontains=filter)

    def barcode(filter):
        return books.filter(metabook__barcode__icontains=filter)

    if field == "any_field":
        # do all the queries and merge them with the | operator
        # all queries being |'d must be either distinct or non-distinct
        return title(filter).distinct() |\
               author(filter).distinct() |\
               course(filter).distinct() |\
               ref(filter).distinct() |\
               status(filter).distinct() |\
               barcode(filter).distinct()
    elif field == "title":
        return title(filter)
    elif field == "author":
        return author(filter)
    elif field == "course_code":
        return course(filter)
    elif field == "ref":
        return ref(filter)
    elif field == "status":
        return status(filter)
    elif field == 'barcode':
        return barcode(filter)
    else:
        return books

def book_sort(field, dir):
    if dir == 'desc': dir = '-'
    else: dir = ''
    return Book.objects.order_by("%s%s" % (dir, field))

def metabook_sort(field, dir):
    if dir == 'desc': dir = '-'
    else: dir = ''
    return MetaBook.objects.order_by("%s%s" % (dir, field))
