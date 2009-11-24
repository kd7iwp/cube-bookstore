from cube.books.models import Book, Listing
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

PER_PAGE = '30'
PAGE_NUM = '1'

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

@login_required()
def listings(request):
    """
    Shows a list of all the books listed.
    Does pagination, sorting and filtering.
    """
    #TODO sorting and filtering!
    listings = Listing.objects.all()
    page_num = get_number(request.GET, 'page', PAGE_NUM)
    listings_per_page = get_number(request.GET, 'per_page', PER_PAGE)

    paginator = Paginator(listings, listings_per_page)
    try:
        page_of_listings = paginator.page(page_num)
    except (EmptyPage, InvalidPage):
        page_of_listings = paginator.page(paginator.num_pages)
    vars = {
        'listings': page_of_listings,
        'per_page': listings_per_page,
        'page': page_num
    }
    return render_to_response('books/listing_list.html', vars, 
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
