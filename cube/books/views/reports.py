# Copyright (C) 2010  Trinity Western University

from cube.books.models import Book
from cube.books.forms import DateRangeForm

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response as rtr
from django.template import RequestContext as RC
from django.http import HttpResponseNotAllowed

@login_required()
def menu(request):
    vars = {
	'date_range_form': DateRangeForm(),
    }
    return rtr('books/reports/menu.html', vars, context_instance=RC(request))

@login_required
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

@login_required
def books_sold_within_date(request):
    """ Shows a list of all books sold within a given date range """
    # TODO Untested!!
    if request.method != "POST": return HttpResponseNotAllowed(['GET'])
    date_range_form = DateRangeForm(request.POST)
    if not date_range_form.is_valid():
        # TODO Untested!
	vars = {
	    'date_range_form' : date_range_form,
	}
	return rtr('books/reports/menu.html', vars, context_instance=RC(request))
	
    to_date = date_range_form.cleaned_data['to_date']
    from_date = date_range_form.cleaned_data['from_date']
    sold_books = Book.objects.filter(status='S', sell_date__gte=from_date).exclude(sell_date__gt=to_date)
    vars = {
	'count' : sold_books.count(),
	'sold_books' : sold_books,
	'from_date' : from_date,
	'to_date' : to_date,
    }
    return rtr('books/reports/books_sold_within_date.html', vars, context_instance=RC(request))
