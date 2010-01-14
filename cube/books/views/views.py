# django imports
from cube.books.models import MetaBook, Course, Listing, Log
from cube.books.forms import BookAndListingForm, MetaBookForm, ListingForm,\
                             FilterForm
from cube.books.views.tools import metabook_sort, listing_filter,\
                                  listing_sort, get_number, tidy_error,\
                                  house_cleaning
from cube.twupass.tools import import_user
from cube.books.email import send_missing_emails, send_sold_emails,\
                             send_tbd_emails
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import HttpResponseRedirect, HttpResponse,\
                        HttpResponseNotAllowed
from django.shortcuts import render_to_response as rtr
from django.template import RequestContext as RC

#python imports
from datetime import datetime
from decimal import Decimal

# pagination defaults
PER_PAGE = '30'
PAGE_NUM = '1'

@login_required()
def listings(request):
    """
    Shows a list of all the books listed.
    Does pagination, sorting and filtering.
    """
    house_cleaning()
    # Filter for the search box
    if request.method == 'GET':
        filter_form = FilterForm(request.GET)
        if filter_form.is_valid():
            cd = filter_form.cleaned_data
            all_listings = Listing.objects.all()
            listings = listing_filter(cd['filter'], cd['field'], all_listings)
        elif request.GET.has_key("sort_by") and request.GET.has_key("dir"):
            listings = listing_sort(request.GET["sort_by"], request.GET["dir"])
        else:
            listings = Listing.objects.all()

    # Filter according to permissions
    if not request.user.is_staff:
        # Non staff can only see listings which are for sale.
        listings = filter(lambda x: x.status == 'F', listings)

    # Pagination
    page_num = get_number(request.GET, 'page', PAGE_NUM)
    listings_per_page = get_number(request.GET, 'per_page', PER_PAGE)

    paginator = Paginator(listings, listings_per_page)
    try:
        page_of_listings = paginator.page(page_num)
    except (EmptyPage, InvalidPage):
        page_of_listings = paginator.page(paginator.num_pages)

    # Template time
    if request.GET.get('dir', '') == 'asc': dir = 'desc'
    else: dir = 'asc'
    vars = {
        'listings' : page_of_listings,
        'per_page' : listings_per_page,
        'page' : page_num,
        'field' : request.GET.get('field', 'any_field'),
        'filter_text' : request.GET.get('filter', ''),
        'dir' : dir
    }
    return rtr('books/listing_list.html', vars, context_instance=RC(request))
@login_required()
def update_listing(request):
    """
    This view is used to update listing data
    """
    bunch = Listing.objects.none()
    action = request.POST.get("Action", '')

    for key, value in request.POST.items():
        if "idToEdit" in key:
            bunch = bunch | Listing.objects.filter(pk=int(value))
            
    if action == "Delete":
        bunch = bunch.exclude(status='D')
        for listing in bunch:
            Log(action='D', listing=listing, who=request.user).save()
        vars = { 'num_deleted': bunch.count() }
        bunch.update(status='D')
        template = 'books/update_listing/deleted.html'
        return rtr(template, vars, context_instance=RC(request))
    elif action[:1] == "To Be Deleted"[:1]:
        # apparently some browsers have issues passing spaces
        # can't do this for Deleted, Seller Paid, and Sold Books
        bunch = bunch.exclude(status__in='DPS')
        send_tbd_emails(bunch)
        for listing in bunch:
            Log(action='T', listing=listing, who=request.user).save()
        vars = {
            'num_doomed' : bunch.count(),
            'num_owners' : len(set(map(lambda x: x.seller, bunch))),
        }
        bunch.update(status='T')
        template = 'books/update_listing/to_be_deleted.html'
        return rtr(template, vars, context_instance=RC(request))
    elif action == "Sold":
        # Allow only if For Sale or On Hold
        bunch = bunch.filter(status__in='FO')
        for listing in bunch:
            Log(action='S', listing=listing, who=request.user).save()
        send_sold_emails(list(bunch))
        vars = {
            'sold' : bunch.count(),
            'num_owners' : len(set(map(lambda x: x.seller, bunch))),
        }
        bunch.update(status='S', sell_date=datetime.today())
        template = 'books/update_listing/sold.html'
        return rtr(template, vars, context_instance=RC(request))
    elif action[:5] == "Seller Paid"[:5]:
        # apparently some browsers have issues passing spaces
        # only staff can do this
        if not request.user.is_staff: bunch = Listing.objects.none()
        # A Seller can be paid only after the book was sold
        else: bunch = bunch.filter(status='S')

        for listing in bunch:
            Log(action='P', listing=listing, who=request.user).save()
        vars = {'paid' : bunch.count()}
        bunch.update(status='P')
        template = 'books/update_listing/seller_paid.html'
        return rtr(template, vars, context_instance=RC(request))
    elif action == "Missing":
        # Must be For Sale, On Hold or To Be Deleted for it to go Missing
        bunch = bunch.filter(status__in='FOT')
        for listing in bunch:
            Log(action='M', listing=listing, who=request.user).save()
        send_missing_emails(bunch)
        vars = {
            'num_owners' : len(set(map(lambda x: x.seller, bunch))),
            'num_missing' : bunch.count(),
        }
        bunch.update(status='M')
        template = 'books/update_listing/missing.html'
        return rtr(template, vars,  context_instance=RC(request))
    elif action[:4] == "Place on Hold"[:4]:
        # apparently some browsers have issues passing spaces
        extended = bunch.filter(status='O', holder=request.user)
        new_hold = bunch.filter(status='F')
        failed = bunch.exclude(status__in='OF', holder=request.user)
        for listing in new_hold:
            Log(action='O', listing=listing, who=request.user).save()
        for listing in extended:
            Log(action='X', listing=listing, who=request.user).save()
        held = extended | new_hold
        vars = {
            'failed' : failed,
            'extended' : extended,
            'new_hold' : new_hold,
            'num_held' : held.count(),
            'total_price' : sum(map(lambda x: x.price, held)),
        }
        extended.update(hold_date = datetime.today())
        new_hold.update(status='O', hold_date=datetime.today(), holder=request.user)
        template = 'books/update_listing/place_hold.html'
        return rtr(template, vars, context_instance=RC(request))
    elif action[:5] == "Remove Holds"[:5]:
        bunch = bunch.filter(status='O')
        if not request.user.is_staff: bunch = bunch.filter(holder=request.user)
        for listing in bunch:
            Log(action='R', listing=listing, who=request.user).save()
        vars = {'removed' : bunch.count()}
        bunch.update(status='F', hold_date=None, holder=None)
        template = 'books/update_listing/remove_holds.html'
        return rtr(template, vars, context_instance=RC(request))
    elif action == "Edit":
        if bunch.count() > 1: too_many = True
        else: too_many = False
        item = bunch[0]
        initial = {
            'seller' : item.seller.id,
            'price' : item.price,
            'barcode' : item.metabook.barcode,
        }
        form = ListingForm(initial=initial)
        logs = Log.objects.filter(listing=item)
        vars = {
            'form' : form,
            'too_many' : too_many,
            'id' : item.id,
            'logs' : logs,
        }
        template = 'books/update_listing/edit.html'
        return rtr(template, vars, context_instance=RC(request))
    else:
        vars = {'action' : action}
        template = 'books/update_listing/error.html'
        return rtr(template, vars, context_instance=RC(request))
@login_required()
def update_listing_edit(request):
    """
    Applies changes to a listing made on the edit page
    If the barcode doesn't exist,
    it makes the user create a Book object as well
    """
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            id = request.POST.get('IdToEdit')
            try:
                listing = Listing.objects.get(id=id)
            except Listing.DoesNotExist:
                message = 'Listing with ref# "%s" does not exist' % id
                return tidy_error(request, message)
            try:
                barcode = form.cleaned_data['barcode']
                listing.metabook = Book.objects.get(barcode=barcode)
            except MetaBook.DoesNotExist:
                # barcode doesn't exist in db, we have to create a metabook.
                initial = {
                    'barcode': barcode,
                    'seller' : form.cleaned_data['seller'],
                    'price' : form.cleaned_data['price'],
                    'listing_id' : listing.id
                }
                form = BookAndListingForm(initial=initial)
                vars = {'form' : form}
                template = 'books/attach_book.html'
                return rtr(template, vars, context_instance=RC(request))
            try:
                seller_id = form.cleaned_data['seller']
                listing.seller = User.objects.get(id=seller_id)
            except User.DoesNotExist:
                user = import_user(seller_id)
                if user == None:
                    message = "Invalid Student ID: %s" % id
                    return tidy_error(request, message)
                listing.seller = user
            listing.price = form.cleaned_data['price']
            listing.save()
            Log(who=request.user, action='E', listing=listing).save()
            vars = {'listing' : listing}
            template = 'books/update_listing/edited.html'
            return rtr(template, vars, context_instance=RC(request))
                
        elif request.POST.get('IdToEdit'):
            # form isn't valid, but we have an id to work with. send user back
            id = request.POST.get('IdToEdit')
            vars = {
                'form' : form,
                'too_many' : False,
                'id' : id,
                'logs' : Log.objects.filter(listing=id),
            }
            template = 'books/update_listing/edit.html'
            return rtr(template, vars, context_instance=RC(request))
    # form isn't valid and we don't have an id so there is nothing we can do
    return HttpResponseNotAllowed(['POST'])

@login_required()
def attach_book(request):
    if request.method == 'POST':
        form = BookAndListingForm(request.POST)
        if form.is_valid():
            # shorten our code line lengths below
            goc = Course.objects.get_or_create
            cd = form.cleaned_data

            # Get the course if it exists, otherwise create it.
            tpl = goc(department=cd['department'], number=cd['course_number'])
            course = tpl[0]

            metabook = MetaBook()
            metabook.title = form.cleaned_data['title']
            metabook.author = form.cleaned_data['author']
            metabook.barcode = form.cleaned_data['barcode']
            metabook.edition = form.cleaned_data['edition']
            metabook.save()
            metabook.courses.add(course)
            metabook.save()

            listing = Listing.objects.get(pk=form.cleaned_data['listing_id'])
            listing.metabook = metabook
            listing.save()
            vars = {'listing' : listing}
            template = 'books/attached.html'
            return rtr(template, vars, context_instance=RC(request))
        # The form has bad data. send the user back
        vars = {'form' : form}
        template = 'books/attach_book.html'
        return rtr(template, vars, context_instance=RC(request))
    return HttpResponseNotAllowed(['POST'])

@login_required()
def my_books(request):
    """
    Displays books the user has on hold
    and is selling, sorts by search box, filters, calculates total prices
    """
    #gets users books
    selling = Listing.objects.filter(seller = request.user)  
    holding = Listing.objects.filter(holder = request.user)    
    priceHold = 0
    priceSell = 0
    searched = False
    #calculate totals for book
    for listing in holding:
        priceHold = listing.price + priceHold         
    for listing in selling:
        priceSell = listing.price + priceSell
    
  
    # Filter for the search box
    if request.GET.has_key("filter") and request.GET.has_key("field"):
        # only run the filter if the GET args are there
        selling = listing_filter(request.GET["filter"] , request.GET["field"],
                                  selling)
        holding = listing_filter(request.GET["filter"] , request.GET["field"],
                                  holding)
        searched = True
    # Sorts results by request
    elif request.GET.has_key("sort_by") and request.GET.has_key("dir"):
        holding = listing_sort(request.GET["sort_by"], request.GET["dir"])
        holding = holding.filter(holder = request.user)
    elif request.GET.has_key("sort_with") and request.GET.has_key("dir"):
        selling = listing_sort(request.GET["sort_with"], request.GET["dir"])
        selling = selling.filter(seller = request.user)
   
    vars = {
         'sellP' : selling,
         'holdP' : holding,
         'priceH' : priceHold,
         'priceS' : priceSell,
         'field' : request.GET.get('field', 'any_field'),
         'filter_text' : request.GET.get('filter', ''),
         'search' : searched
    }             
    template = 'books/my_books.html'
    return rtr(template, vars, context_instance=RC(request))    
    
    # Save New User
    if action == "Save":
        role = request.POST.get("role", '')
        try:
            user = User.objects.get(id = student_id)
        except User.DoesNotExist:
            user = import_user(student_id)
            if user == None:
                message = "Invalid Student ID: %s" % student_id
                return tidy_error(request, message)
        if request.POST.get("role", '') == "Administrator":
            user.is_superuser = True
            user.is_staff = True
            user.save()
        else:
            user.is_superuser = False
            user.is_staff = True
            user.save()
        vars = {
            'user_name' : user.get_full_name(),
            'administrator' : user.is_superuser,
        }
        template = 'books/update_staff/saved.html'
        return rtr(template, vars, context_instance=RC(request))

@login_required()
def add_listing(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            student_id = form.cleaned_data['seller']
            price = form.cleaned_data['price']
            barcode = form.cleaned_data['barcode']
            try:
                metabook = MetaBook.objects.get(barcode=barcode)
            except MetaBook.DoesNotExist: 
                initial = {
                    'barcode' : barcode,
                    'seller' : student_id,
                    'price' : price
                }
                form = BookAndListingForm(initial=initial)
                vars = {'form' : form}
                template = 'books/add_listing_and_book.html'
                return rtr(template, vars, context_instance=RC(request))
            try:
                seller = User.objects.get(id=student_id)
            except User.DoesNotExist:
                seller = import_user(student_id)
                if seller == None:
                    message = "Invalid Student ID: %s" % student_id
                    return tidy_error(request, message)
            listing = Listing(price=price, status="F", metabook=metabook, seller=seller)
            listing.save()
            Log(listing=listing, who=request.user, action='A').save()
            vars = {
                'title' : metabook.title,
                'listing_id' : listing.id
            }
            template = 'books/update_listing/added.html'
            return rtr(template, vars, context_instance=RC(request))
        # the form isn't valid. send the user back.
        vars = {'form' : form}
        template = 'books/add_listing.html'
        return rtr(template, vars, context_instance=RC(request))
    else:
        # the user is hitting the page for the first time
        form = ListingForm()
        vars = {'form' : form}
        template = 'books/add_listing.html'
        return rtr(template, vars, context_instance=RC(request))

def add_listing_and_book(request):
    if request.method == "POST":
        if request.POST.get("Action", '') == 'Add':
            form = BookAndListingForm(request.POST)
            if form.is_valid():
                # This came from the add_book view, and we need to
                # create a book and a listing
                barcode = form.cleaned_data['barcode']
                price = form.cleaned_data['price']
                sid = form.cleaned_data['seller']
                author = form.cleaned_data['author']
                title = form.cleaned_data['title']
                ed = form.cleaned_data['edition']
                dept = form.cleaned_data['department']
                course_num = form.cleaned_data['course_number']

                metabook = MetaBook(barcode=barcode, author=author, title=title, edition=ed)
                metabook.save()
                goc = Course.objects.get_or_create
                course, created = goc(department=dept, number=course_num)
                metabook.courses.add(course)
                metabook.save()
                try:
                    seller = User.objects.get(pk=sid)
                except User.DoesNotExist:
                    seller = import_user(sid)
                    if seller == None:
                        message = "Invalid Student ID: %s" % sid
                        return tidy_error(request, message)
                listing = Listing(seller=seller, price=Decimal(price), metabook=metabook)
                listing.status = 'F'
                listing.save()
                Log(listing=listing, who=request.user, action='A').save()

                vars = {
                    'title' : metabook.title,
                    'author' : metabook.author,
                    'seller_name' : seller.get_full_name()
                }
                template = 'books/update_book/added.html'
                return rtr(template, vars, context_instance=RC(request))
            vars = {'form' : form}
            template = 'books/add_listing_and_book.html'
            return rtr(template, vars, context_instance=RC(request))

@login_required()
def list_books(request):
    """
    List all books in the database
    """
    # TODO allow non-staff to view this?
    if request.GET.has_key("sort_by") and request.GET.has_key("dir"):
        metabooks = book_sort(request.GET["sort_by"], request.GET["dir"])
    else: metabooks = MetaBook.objects.all()

    # Pagination
    page_num = get_number(request.GET, 'page', PAGE_NUM)
    metabooks_per_page = get_number(request.GET, 'per_page', PER_PAGE)

    paginator = Paginator(metabooks, metabooks_per_page)
    try:
        page_of_metabooks = paginator.page(page_num)
    except (EmptyPage, InvalidPage):
        page_of_metabooks = paginator.page(paginator.num_pages)

    # Template time
    if request.GET.get('dir', '') == 'asc': dir = 'desc'
    else: dir = 'asc'
    vars = {
        'metabooks' : page_of_metabooks,
        'per_page' : metabooks_per_page,
        'page' : page_num,
        'dir' : 'desc' if request.GET.get('dir', '') == 'asc' else 'asc'
    }

    template = 'books/list_books.html'
    return rtr(template, vars, context_instance=RC(request))
@login_required()
def update_books(request):
    """
    This view is used to update book data
    """
    bunch = MetaBook.objects.none()
    if request.method == "POST":
        action = request.POST.get("Action", '')
    else:
        return HttpResponseNotAllowed(['POST'])

    for key, value in request.POST.items():
        if "idToEdit" in key:
            bunch = bunch | MetaBook.objects.filter(pk=int(value))
            
    if action == "Delete":
        bunch = bunch.exclude(status='D')
        vars = {'num_deleted': bunch.count()}
        bunch.update(status='D')
        template = 'books/update_listing/deleted.html'
        return rtr(template, vars, context_instance=RC(request))
    elif action == "Edit":
        if bunch.count() > 1: too_many = True
        else: too_many = False
        item = bunch[0]
        form = MetaBookForm(instance=item)
        vars = {
            'form' : form,
            'metabook_id' : item.id,
        }
        template = 'books/edit_book.html'
        return rtr(template, vars, context_instance=RC(request))
    elif action == "Save":
        metabook_id = request.POST.get('metabook_id', '')
        metabook = MetaBook.objects.get(pk=metabook_id)
        form = MetaBookForm(request.POST, instance=metabook)
        if form.is_valid():
            form.save()
            vars={'metabook': metabook}
            template = 'books/update_book/saved.html'
            return rtr(template, vars, context_instance=RC(request))
        # the form isn't valid. send the user back
        vars = {'form' : form}
        template = 'books/edit_book.html'
        return rtr(template, vars, context_instance=RC(request))
    else:
        vars = {'action' : action}
        template = 'books/update_listing/error.html'
        return rtr(template, vars, context_instance=RC(request))

