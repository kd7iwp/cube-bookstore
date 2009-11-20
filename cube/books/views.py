from django.contrib.auth.decorators import login_required
from cube.books.models import Book, Listing
from django.views.generic.list_detail import object_list
from django.http import HttpResponseRedirect, HttpResponse
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
# http://docs.djangoproject.com/en/dev/topics/auth/#handling-authorization-in-custom-backends

@login_required()
def listings(request):
    #if not request.user.is_authenticated():
    #    return HttpResponseRedirect(LOGIN_URL)
    #return object_list(*args, **kwargs)
    listings = Listing.objects.all()
    return render_to_response('books/listing_list.html', {'listings': listings},
                              context_instance=RequestContext(request))

def myBooksies(request):
    if request.user.is_authenticated():
        #john = request.user.last_name
        
        work = Listing.objects.filter(seller = request.user)
        me = request.user
	 
        #need title, author, price, course code, ref#
        return HttpResponse(me)    
    else:
        return HttpResponse("No work")
