from cube.books.models import Book, Listing
from cube.books.view_tools import listing_filter, listing_sort, get_number
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from django.template import RequestContext
from django.contrib.auth.models import User

# pagination defaults
PER_PAGE = '30'
PER_PAGE_STAFF = '20'
PAGE_NUM = '1'

@login_required()
def listings(request):
    """
    Shows a list of all the books listed.
    Does pagination, sorting and filtering.
    """
    if request.GET.has_key("filter") and request.GET.has_key("field"):
        # only run the filter if the GET args are there
        listings = listing_filter(request.GET["filter"] , request.GET["field"],
                                  Listing.objects.all())
    elif request.GET.has_key("sort_by") and request.GET.has_key("dir"):
        listings = listing_sort(request.GET["sort_by"], request.GET["dir"])
    else:
        listings = Listing.objects.all()

    page_num = get_number(request.GET, 'page', PAGE_NUM)
    listings_per_page = get_number(request.GET, 'per_page', PER_PAGE)

    paginator = Paginator(listings, listings_per_page)
    try:
        page_of_listings = paginator.page(page_num)
    except (EmptyPage, InvalidPage):
        page_of_listings = paginator.page(paginator.num_pages)
    vars = {
        'listings' : page_of_listings,
        'per_page' : listings_per_page,
        'page' : page_num,
        'field' : request.GET.get('field', 'any_field'),
        'filter_text' : request.GET.get('filter', ''),
        'dir' : 'desc' if request.GET.get('dir', '') == 'asc' else 'asc'
    }
    return render_to_response('books/listing_list.html', vars, 
                              context_instance=RequestContext(request))
@login_required()
def update_data(request):
    """
    This view is used to update book data
    """
    def singlural(number):
        """
        Returns appropriate text depending on the singularity of the number
        """
        if number == 1: return "1 item has been"
        return "%s items have been" % number

    def set_statuses(status, listings):
        """
        Sets a status on all listings given and saves them
        """
        for listing in listings:
            listing.status = status
            listing.save()

    edit = []
    action = request.POST.get("Action", '')
    singular = "item has been"
    plural = "items have been"

    for key, value in request.POST.items():
        if "idToEdit" in key:
            edit.append(Listing.objects.get(pk=int(value)))
            
    if action == "Delete":
        set_statuses('D', edit)
        message = "%s deleted." % singlural(len(edit))
    elif action[:1] == "To Be Deleted"[:1]:
        # apparently some browsers have issues passing spaces
        # TODO add bells and whistles
        set_statuses('T', edit)
        message = "%s marked as 'To Be Deleted'." % singlural(len(edit))
    elif action == "Sold":
        set_statuses('S', edit)
        #TODO implement email and the bells and whistles
        message = "%s set to Sold and the owners have been emailed " +\
                  "and asked to come pickup the money." % singlural(len(edit))
    elif action[:5] == "Seller Paid"[:5]:
        # apparently some browsers have issues passing spaces
        # TODO add the bells and whistles
        set_statuses('P', edit)
        message = "%s set to Seller Paid" % singlural(len(edit))
    elif action[:4] == "Place on Hold"[:4]:
        # apparently some browsers have issues passing spaces
        # TODO add the bells and whistles
        set_statuses('O', edit)
        message = "Under Construction..."
    #elif action == "Missing":

    vars = {
        'message' : message, 
    }
    return render_to_response('books/listing_edit.html', vars, 
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

def staff(request):
    """
    Shows a list of all staff
    """
    listings = User.objects.filter(is_staff = True)
    page_num = get_number(request.GET, 'page', PAGE_NUM)
    listings_per_page = get_number(request.GET, 'per_page', PER_PAGE_STAFF)
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
    return render_to_response('staff/staff.html', vars, 
                              context_instance=RequestContext(request))

def staffedit(request):
    """
    Shows a list of all staff
    """
    listings = User.objects.filter(is_staff = True)
    page_num = get_number(request.GET, 'page', PAGE_NUM)
    listings_per_page = get_number(request.GET, 'per_page', PER_PAGE_STAFF)
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
    return render_to_response('staff/staffedit.html', vars, 
                              context_instance=RequestContext(request))
