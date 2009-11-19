from cube.books.models import Book
from cube.books.models import Listing
from django.http import HttpResponse
from django.shortcuts import render_to_response

def myBooksies(request):
    if request.user.is_authenticated():
        #john = request.user.last_name
        
        work = Listing.objects.filter(seller = request.user)
        me = request.user
	 
        #need title, author, price, course code, ref#
        return HttpResponse(me)    
    else:
        return HttpResponse("No work")


