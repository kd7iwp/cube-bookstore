# Copyright (C) 2010  Trinity Western University

from cube.books.models import Book

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response as rtr
from django.template import RequestContext as RC

@login_required()
def menu(request):
    return rtr('books/reports/menu.html', {}, context_instance=RC(request))

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
