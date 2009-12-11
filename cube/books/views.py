# django imports
from cube.books.models import Book, Listing
from cube.books.view_tools import listing_filter, listing_sort, get_number
from cube.books.email import send_missing_emails
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from django.template import RequestContext
from django.contrib.auth.models import User

#python imports
from datetime import datetime

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

    def set_bunch(attr, value):
        """
        Sets a status on all listings given and saves them
        """
        for listing in bunch:
            setattr(listing, attr, value)
            listing.save()

    messages = []
    bunch = []
    action = request.POST.get("Action", '')
    singular = "item has been"
    plural = "items have been"

    for key, value in request.POST.items():
        if "idToEdit" in key:
            bunch.append(Listing.objects.get(pk=int(value)))
            
    if action == "Delete":
        set_bunch('status', 'D')
        messages.append("%s deleted." % singlural(len(bunch)))
    elif action[:1] == "To Be Deleted"[:1]:
        # apparently some browsers have issues passing spaces
        # TODO add bells and whistles
        set_bunch('status', 'T')
        messages.append("%s marked as 'To Be Deleted'." % singlural(len(bunch)))
    elif action == "Sold":
        set_bunch('status', 'S')
        #TODO implement email and the bells and whistles
        messages.append("%s set to Sold and the owners " %\
                        singlural(len(bunch)) +\
                        "have been emailed and asked to come pickup the money.")
    elif action[:5] == "Seller Paid"[:5]:
        # apparently some browsers have issues passing spaces
        # TODO add the bells and whistles
        set_bunch('status', 'P')
        messages.append("%s set to Seller Paid." % singlural(len(bunch)))
    elif action == "Missing":
        # only non-missing ones can be set to missing
        bunch = filter(lambda x : x.status != 'M', bunch)
        set_bunch('status', 'M')
        send_missing_emails(bunch)
        owners = set(map(lambda x: x.seller, bunch)) # unique owners
        messages.append("%s set to Missing " % singlural(len(bunch)) +\
                        "" if len(bunch) == 0 else\
                        ("and the owner%s been notified via email." %\
                        (" has" if len(owners) == 1 else "s have")))
    elif action[:4] == "Place on Hold"[:4]:
        # apparently some browsers have issues passing spaces
        def hold_filter(x):
            """
            Only let listings which are For Sale or already On Hold
            be Placed on Hold
            """
            if x.get_status_display() == 'On Hold' and x.holder == request.user:
                messages.append('"%s" has been placed ' % x.book.title +\
                                "on hold for another 24 hours. $%s" % x.price)
                return x
            elif x.get_status_display() != 'For Sale':
                messages.append('"%s"' % x.book.title +\
                                'was marked %s ' % x.get_status_display() +\
                                "just before you requested it.")
            else:
                messages.append('"%s" has been reserved ' % x.book.title +\
                                "for you for 24 hours. $%s" % x.price)
                return x

        bunch = filter(hold_filter, bunch)
        set_bunch('status', 'O')
        set_bunch('hold_date', datetime.today())
        messages.append("Total: $%s" % sum(map(lambda x: x.price, bunch)))
        messages.append("Please pickup your Requested Books within the next" +\
                        ' 24 hours from the "Cube" which is by the cafeteria.')
    elif action[:5] == "Remove Holds"[:5]:
        def rm_hold_filter(x):
            """ 
            Filters listings through if the current user is staff
            or the holder is the current user and the status is 'On Hold'
            """
            if x.status == 'O':
                if request.user.is_staff: return x
                if x.holder == request.user: return x
        
        bunch = filter(rm_hold_filter, bunch)
        set_bunch('status', 'F') # set to "For Sale"
        set_bunch('hold_date', None)
        messages.append("%s hold%s been removed." % (len(bunch),
            ' has' if len(bunch) == 1 else 's have'))
    else:
        # TODO edit
        messages.append("Something went wrong... talk to whoever is in charge")
    vars = {
        'messages' : messages, 
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
