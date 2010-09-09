# Copyright (C) 2010  Trinity Western University

from cube.books.models import Book, MetaBook, Log
from cube.books.forms import DateRangeForm
from cube.twupass.tools import import_user
from cube.books.views.tools import tidy_error

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response as rtr
from django.template import RequestContext as RC
from django.http import HttpResponseNotAllowed
from django.contrib.auth.models import User

@login_required()
def menu(request):
    vars = {
	'date_range_form': DateRangeForm(),
    }
    return rtr('books/reports/menu.html', vars, context_instance=RC(request))

@login_required()
def per_status(request):
    """ Shows the number of books per status """
    vars = {
	"for_sale" : Book.objects.filter(status='F').count(),
	"missing" : Book.objects.filter(status='M').count(),
	"on_hold" : Book.objects.filter(status='O').count(),
	"seller_paid" : Book.objects.filter(status='P').count(),
	"sold" : Book.objects.filter(status='S').count(),
	"to_be_deleted" : Book.objects.filter(status='T').count(),
	"deleted" : Book.objects.filter(status='D').count(),
    }
    return rtr('books/reports/per_status.html', vars, context_instance=RC(request))

@login_required()
def books_sold_within_date(request):
    """ Shows a list of all books sold within a given date range """
    if request.method != "POST": return HttpResponseNotAllowed(['GET'])
    date_range_form = DateRangeForm(request.POST)
    if not date_range_form.is_valid():
	vars = {
	    'date_range_form' : date_range_form,
	}
	return rtr('books/reports/menu.html', vars, context_instance=RC(request))
	
    to_date = date_range_form.cleaned_data['to_date']
    from_date = date_range_form.cleaned_data['from_date']
    book_sale_logs = Log.objects.filter(action='S', when__gte=from_date).exclude(when__gt=to_date)
    vars = {
	'book_sale_logs' : book_sale_logs.order_by('book__sell_date'),
	'from_date' : from_date,
	'to_date' : to_date,
    }
    return rtr('books/reports/books_sold_within_date.html', vars, context_instance=RC(request))

@login_required()
def user(request, user_id):
    if request.method == "POST": return HttpResponseNotAllowed(['POST'])
    try:
        user_obj = User.objects.get(id=user_id)
    except User.DoesNotExist:
        user_obj = import_user(user_id)
	if user == None:
	    message = "Invalid Student ID: %s" % user_id
	    return tidy_error(request, message)
    logs_of_books_for_sale = Log.objects.filter(book__seller=user_obj).filter(action='A')
    vars = {
	'user_obj' : user_obj,
	'logs' : Log.objects.filter(who=user_obj).order_by('when'),
	'logs_of_books_for_sale' : logs_of_books_for_sale,
    }
    return rtr('books/reports/user.html', vars, context_instance=RC(request))

@login_required()
def book(request, book_id):
    if request.method == "POST": return HttpResponseNotAllowed(['POST'])
    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
	message = "Invalid Book Ref #: %s" % book_id
	return tidy_error(request, message)
    vars = {
	'book' : book,
	'logs' : Log.objects.filter(book=book),
    }
    return rtr('books/reports/book.html', vars, context_instance=RC(request))

@login_required()
def metabook(request, metabook_id):
    if request.method == "POST": return HttpResponseNotAllowed(['POST'])
    try:
        metabook = MetaBook.objects.get(id=metabook_id)
    except MetaBook.DoesNotExist:
	message = "Invalid MetaBook Ref #: %s" % metabook_id
	return tidy_error(request, message)
    vars = {
	'metabook' : metabook,
	'books' : Book.objects.filter(metabook=metabook).order_by('list_date'),
    }
    return rtr('books/reports/metabook.html', vars, context_instance=RC(request))

@login_required()
def holds_by_user(request):
    if request.method == "POST": return HttpResponseNotAllowed(['POST'])
    books_on_hold = Book.objects.filter(status='O')
    user_dict = {}
    for book in books_on_hold:
        if not user_dict.has_key(book.holder):
            user_dict[book.holder] = Book.objects.filter(status='O', holder=book.holder).count()
    user_list_by_user = user_dict.items()
    user_list_by_count = []
    for item in user_list_by_user:
        user_list_by_count.append((item[1], item[0]))
    user_list_by_count.sort(reverse=True)
    vars = {'user_list': user_list_by_count}
    return rtr('books/reports/holds_by_user.html', vars, context_instance=RC(request))
