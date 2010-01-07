# django imports
from cube.books.models import Book, Course, Listing, Log
from cube.books.view_tools import book_sort, listing_filter,\
                                  listing_sort, get_number
from cube.books.email import send_missing_emails, send_sold_emails,\
                             send_tbd_emails
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

#python imports
from datetime import datetime
from decimal import Decimal

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
    # Filter for the search box
    if request.GET.has_key("filter") and request.GET.has_key("field"):
        # only run the filter if the GET args are there
        listings = listing_filter(request.GET["filter"] , request.GET["field"],
                                  Listing.objects.all())
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
        vars = { 'num_deleted': bunch.count() }
        bunch.update(status='D')
        return render_to_response('books/update_listing/deleted.html', vars,
                                    context_instance=RequestContext(request))
    elif action[:1] == "To Be Deleted"[:1]:
        # apparently some browsers have issues passing spaces
        # TODO add bells and whistles
        # can't do this for Deleted, Seller Paid, and Sold Books
        bunch = bunch.exclude(status__in='DPS')
        send_tbd_emails(bunch)
        vars = {
            'num_doomed' : bunch.count(),
            'num_owners' : len(set(map(lambda x: x.seller, bunch))),
        }
        bunch.update(status='T')
        return render_to_response('books/update_listing/to_be_deleted.html', vars,
                                  context_instance=RequestContext(request))
    elif action == "Sold":
        # Allow only if For Sale or On Hold
        bunch = bunch.filter(status__in='FO')
        send_sold_emails(list(bunch))
        vars = {
            'sold' : bunch.count(),
            'num_owners' : len(set(map(lambda x: x.seller, bunch))),
        }
        bunch.update(status='S', sell_date=datetime.today())
        return render_to_response('books/update_listing/sold.html', vars, 
                                  context_instance=RequestContext(request))
    elif action[:5] == "Seller Paid"[:5]:
        # apparently some browsers have issues passing spaces

        # only staff can do this
        if not request.user.is_staff: bunch = Listing.objects.none()
        # A Seller can be paid only after the book was sold
        else: bunch = bunch.filter(status='S')

        vars = {'paid' : bunch.count()}
        bunch.update(status='P')
        return render_to_response('books/update_listing/seller_paid.html', vars, 
                                  context_instance=RequestContext(request))
    elif action == "Missing":
        # Must be For Sale, On Hold or To Be Deleted for it to go Missing
        bunch = bunch.filter(status__in='FOT')
        send_missing_emails(bunch)
        vars = {
            'num_owners' : len(set(map(lambda x: x.seller, bunch))),
            'num_missing' : bunch.count(),
        }
        bunch.update(status='M')
        return render_to_response('books/update_listing/missing.html', vars, 
                                  context_instance=RequestContext(request))
    elif action[:4] == "Place on Hold"[:4]:
        # apparently some browsers have issues passing spaces
        extended = bunch.filter(status='O', holder=request.user)
        new_hold = bunch.filter(status='F')
        failed = bunch.exclude(status__in='OF', holder=request.user)
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
        return render_to_response('books/update_listing/place_hold.html', vars, 
                                  context_instance=RequestContext(request))
    elif action[:5] == "Remove Holds"[:5]:
        bunch = bunch.filter(status='O')
        if not request.user.is_staff: bunch = bunch.filter(holder=request.user)
        vars = {'removed' : bunch.count()}
        bunch.update(status='F', hold_date=None, holder=None)
        return render_to_response('books/update_listing/remove_holds.html', vars,
                                  context_instance=RequestContext(request))
    elif action == "Edit":
        too_many = True if bunch.count() > 1 else False
        item = bunch[0]
        rows = [{'name' : 'Bar Code', 'value' : item.book.barcode},
                {'name' : 'Student ID', 'value' : item.seller.id},
                {'name' : 'Price', 'value' : item.price},
                {'name' : 'Buyer Student ID', 'value' : item.holder.id if item.holder else ''}]
        vars = {
            'rows' : rows,
            'too_many' : too_many,
            'id' : item.id,
        }
        return render_to_response('books/update_listing/edit.html', vars, 
                                  context_instance=RequestContext(request))
    else:
        vars = {'action' : action}
        return render_to_response('books/update_listing/error.html', vars, 
                                  context_instance=RequestContext(request))
@login_required()
def myBooksies(request):
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
    return render_to_response('myBooks.html', vars,
                              context_instance=RequestContext(request))    
    
@login_required()    
def staff(request):
    users = User.objects.filter(is_staff = True)
    page_num = get_number(request.GET, 'page', PAGE_NUM)
    users_per_page = get_number(request.GET, 'per_page', PER_PAGE_STAFF)
    paginator = Paginator(users, users_per_page)
    try:
        page_of_users = paginator.page(page_num)
    except (EmptyPage, InvalidPage):
        page_of_users = paginator.page(paginator.num_pages)
    vars = {
        'users' : page_of_users,
        'per_page' : users_per_page,
        'page' : page_num,
        'field' : request.GET.get('field', 'any_field'),
        'filter_text' : request.GET.get('filter', ''),
        'dir' : 'desc' if request.GET.get('dir', '') == 'asc' else 'asc'
    }
    return render_to_response('books/staff.html', vars, 
                              context_instance=RequestContext(request))

@login_required()
def update_staff(request):
    # Delete User
    student_id = request.POST.get("student_id", '')
    if request.POST.get("Action", '') == "Delete" and student_id:
        try:
            user = User.objects.get(id = student_id)
            user.is_superuser = False
            user.is_staff = False
            user.save()
            vars = { 'num_deleted' : 1 }
            return render_to_response('books/update_staff/deleted.html', vars, 
                                      context_instance=RequestContext(request))
        except User.DoesNotExist:
            # TODO make an error page to pass messages to
            return HttpResponse("User does not Exist")
    elif request.POST.get("Action", '') == "Delete":
        try:
            num_deleted = 0
            for key, value in request.POST.items():
                if "idToEdit" in key:
                    user = User.objects.get(id = value)  
                    user.is_superuser = False
                    user.is_staff = False
                    user.save()
                    num_deleted += 1
            vars = { 'num_deleted' : num_deleted }
            return render_to_response('books/update_staff/deleted.html', vars, 
                                      context_instance=RequestContext(request))
        except User.DoesNotExist:
            # TODO make an error page to pass messages to
            return HttpResponse("User does not Exist")

    # Save New User
    if request.POST.get("Action", '') == "Save":
        role = request.POST.get("role", '')
        try:
            user = User.objects.get(id = student_id)
            if request.POST.get("role", '') == "Administrator":
                user.is_superuser = True
                user.is_staff = True
                user.save()
            else:
                user.is_superuser = False
                user.is_staff = True
                user.save()
            vars = {
                'user_name' : "%s %s" % (user.first_name, user.last_name),
                'administrator' : user.is_superuser,
            }
            return render_to_response('books/update_staff/saved.html', vars, 
                                      context_instance=RequestContext(request))
        except User.DoesNotExist:
            return HttpResponse("Invalid Student ID")

@login_required()
def staffedit(request):
    """
    Displays an edit page for user permissions
    If the data needs to be updated (e.g. delete or save)
    then it passes the request on to update_staff
    """
    if request.POST.get('Action', '') == "Delete":
        return update_staff(request)
    users = []
    if request.POST.get('Action', '')[:3] == "Add New"[:3]:
        # Apparently some browsers have trouble POSTing spaces
        edit = False
        users.append(User())
    else:
        edit = True
        for key, value in request.POST.items():
            if "idToEdit" in key:
                users.append(User.objects.get(id=value))
        if len(users) == 0:
            # They clicked edit without selecting any users. How silly.
            return staff(request)
    vars = {
        'edit' : edit,
        'too_many' : len(users) > 1,
        'first_name' : users[0].first_name,
        'last_name' : users[0].last_name,
        'student_id' : users[0].id,
        'current_role' : 'admin' if users[0].is_superuser else 'staff',
    }
    return render_to_response('books/staffedit.html', vars, 
                              context_instance=RequestContext(request))

@login_required()
def add_books(request):
    if request.POST.get("student_id") and request.POST.get("Price") and request.POST.get("BarCode"):
        barcode = request.POST.get("BarCode")
        student_id = int(request.POST.get("student_id"))
        price = Decimal(request.POST.get("Price"))
        try:
            book = Book.objects.get(barcode=barcode)
        except Book.DoesNotExist: 
            vars = {
                'barcode' : barcode,
                'student_id' : student_id,
                'price' : price,
                'edition_range' : range(1,51),
            }
            return render_to_response('newBook.html', vars,
                                      context_instance=RequestContext(request))
        try:
            seller = User.objects.get(id=student_id)
        except User.DoesNotExist:
            from cube.twupass.backend import TWUPassBackend
            seller = TWUPassBackend().import_user(student_id)
            if seller == None:
                message = "Invalid Student ID"
                return render_to_response('error.html', {'message' : message },
                                      context_instance=RequestContext(request))
                
        listing = Listing(list_date=datetime.now(), price=price, status="F",
                          book=book, seller=seller)
        listing.save()
        vars = {
            'title' : book.title,
            'listing_id' : listing.id
        }
        return render_to_response('books/update_listing/added.html', vars, 
                                  context_instance=RequestContext(request))
    elif request.POST.get("Action", '') == 'Add':
        # This came from the add_books view, and we need to
        # create a book and a listing
        g = lambda x: request.POST.get(x, '')
        barcode, price, sid, author, title, ed, dept, course_num =\
            g('barcode'), g('price'), int(g('student_id')), g('author'),\
            g('title'), g('edition'), g('department'), g('course_num')
        book = Book(barcode=barcode, author=author, title=title, edition=ed)
        book.save()
        course, created = Course.objects.get_or_create(division=dept,
                                                       number=course_num)
        book.courses.add(course)
        book.save()
        try:
            seller = User.objects.get(pk=sid)
        except User.DoesNotExist:
            from cube.twupass.backend import TWUPassBackend
            seller = TWUPassBackend().import_user(sid)
            if seller == None:
                message = "Invalid Student ID"
                return render_to_response('error.html', {'message' : message },
                                      context_instance=RequestContext(request))
        listing = Listing(seller=seller, price=Decimal(price), book=book)
        listing.status = 'F'
        listing.save()

        vars = {
            'title' : book.title,
            'author' : book.author,
            'seller_name' : "%s %s" % (seller.first_name, seller.last_name),
        }
        return render_to_response('books/update_book/added.html', vars, 
                                  context_instance=RequestContext(request))
    elif request.POST.get("Author"):
        # TODO what is this case for???
        # and request.POST.get("Title") and request.POST.get("Edition") and request.POST.get("Department") and request.POST.get("Course Number"):
        course = request.POST.get("Department") + " " + request.POST.get("Course Number")
        the_author = request.POST.get("Author")
        the_title = request.POST.get("Title")
        the_edition = request.POST.get("Edition")
        new_book = Book(author=the_author, title=the_title, edition=the_edition, courses=course) 
        new_book.save()
        return HttpResponse("happy")
    else:
        # the user is hitting the page for the first time
        return render_to_response('books/add_books.html',
                                  context_instance=RequestContext(request))

@login_required()
def listBooks(request):
    """
    List all books in the database
    """
    # TODO allow non-staff to view this?
    if request.GET.has_key("sort_by") and request.GET.has_key("dir"):
        books = book_sort(request.GET["sort_by"], request.GET["dir"])
    else: books = Book.objects.all()

    # Pagination
    page_num = get_number(request.GET, 'page', PAGE_NUM)
    books_per_page = get_number(request.GET, 'per_page', PER_PAGE)

    paginator = Paginator(books, books_per_page)
    try:
        page_of_books = paginator.page(page_num)
    except (EmptyPage, InvalidPage):
        page_of_books = paginator.page(paginator.num_pages)

    # Template time
    vars = {
        'books' : page_of_books,
        'per_page' : books_per_page,
        'page' : page_num,
        'dir' : 'desc' if request.GET.get('dir', '') == 'asc' else 'asc'
    }

    return render_to_response('books/listBooks.html', vars,
                               context_instance=RequestContext(request))
@login_required()
def update_books(request):
    """
    This view is used to update book data
    """
    bunch = Book.objects.none()
    action = request.POST.get("Action", '')

    for key, value in request.POST.items():
        if "idToEdit" in key:
            bunch = bunch | Book.objects.filter(pk=int(value))
            
    if action == "Delete":
        bunch = bunch.exclude(status='D')
        vars = { 'num_deleted': bunch.count() }
        bunch.update(status='D')
        return render_to_response('books/update_listing/deleted.html', vars,
                                    context_instance=RequestContext(request))
    #elif action == "Edit":
    #    too_many = True if bunch.count() > 1 else False
    #    item = bunch[0]
    #    rows = [{'name' : 'Bar Code', 'value' : item.book.barcode},
    #            {'name' : 'Student ID', 'value' : item.seller.id},
    #            {'name' : 'Price', 'value' : item.price},
    #            {'name' : 'Buyer Student ID', 'value' : item.holder.id}]
    #    vars = {
    #        'rows' : rows,
    #        'too_many' : too_many,
    #        'id' : item.id,
    #    }
    #    return render_to_response('books/update_listing/edit.html', vars, 
    #                              context_instance=RequestContext(request))
    else:
        vars = {'action' : action}
        return render_to_response('books/update_listing/error.html', vars, 
                                  context_instance=RequestContext(request))

