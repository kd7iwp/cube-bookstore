# Copyright (C) 2010  Trinity Western University

# django imports
from cube.books.models import MetaBook, Course, Book, Log
from cube.books.forms import NewBookForm, BookForm, FilterForm 
from cube.books.views.tools import book_filter,\
                                  book_sort, get_number, tidy_error,\
                                  house_cleaning
from cube.twupass.tools import import_user
from cube.books.email import send_missing_emails, send_sold_emails,\
                             send_tbd_emails
from cube.books.http import HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import HttpResponseRedirect, HttpResponse,\
                        HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import render_to_response as rtr
from django.template import loader, RequestContext as RC

#python imports
from datetime import datetime
from decimal import Decimal

# pagination defaults
PER_PAGE = '30'
PAGE_NUM = '1'

@login_required()
def book_list(request):
    """
    Shows a list of all the books listed.
    Does pagination, sorting and filtering.
    
    Tests:
        - GETTest
        - SearchBookTest
        - SortBookTest
    """
    house_cleaning()
    # Filter for the search box
    if request.method == 'GET':
        filter_form = FilterForm(request.GET)
        if filter_form.is_valid():
            cd = filter_form.cleaned_data
            all_books = Book.objects.all()
            books = book_filter(cd['filter'], cd['field'], all_books)
        elif request.GET.has_key("sort_by") and request.GET.has_key("dir"):
            books = book_sort(request.GET["sort_by"], request.GET["dir"])
        else:
            books = Book.objects.all()

    # Filter according to permissions
    if not request.user.is_staff:
        # Non staff can only see books which are for sale.
        books = filter(lambda x: x.status == 'F', books)

    # Pagination
    page_num = get_number(request.GET, 'page', PAGE_NUM)
    books_per_page = get_number(request.GET, 'per_page', PER_PAGE)

    paginator = Paginator(books, books_per_page)
    try:
        page_of_books = paginator.page(page_num)
    except (EmptyPage, InvalidPage):
        page_of_books = paginator.page(paginator.num_pages)

    # Template time
    if request.GET.get('dir', '') == 'asc': dir = 'desc'
    else: dir = 'asc'
    var_dict = {
        'books' : page_of_books,
        'per_page' : books_per_page,
        'page' : page_num,
        'field' : request.GET.get('field', 'any_field'),
        'filter_text' : request.GET.get('filter', ''),
        'dir' : dir
    }
    return rtr('books/book_list.html', var_dict, context_instance=RC(request))

@login_required()
def delete_book(request):
    """
    This view deletes a book passed to it

    Takes values
        - book
        - action = delete
    """
    if not request.user.is_staff:
        t = loader.get_template('403.html')
        c = RC(request)
        return HttpResponseForbidden(t.render(c))
    for key in ['book', 'action']:
        if not request.POST.has_key(key):
            var_dict = {
                'message' : "Missing key %s" % key
            }
            t = loader.get_template('400.html')
            c = RC(request, var_dict)
            return HttpResponseBadRequest(t.render(c))
        id_to_edit = request.POST.get('IdToEdit')
    try:
        book = Book.objects.get(id=request.POST.get('book'))
    except Book.DoesNotExist:
        message = 'Book with ref# "%s" does not exist' % id_to_edit
        return tidy_error(request, message)
    Log(action='D', book=book, who=request.user).save()
    book.status='D'
    book.save()
    var_dict = { 
        'refno': book.id
    }
    template = 'books/deleted.html'
    return rtr(template, var_dict, context_instance=RC(request))

@login_required()
def update_book(request):
    """
    This view is used to update book data
    
    Tests:
        - GETTest
        - EmailTest
        - HoldGlitchTest
        - NotAllowedTest
    """
    if not request.method == "POST":
        t = loader.get_template('405.html')
        c = RC(request)
        return HttpResponseNotAllowed(t.render(c), ['POST'])
    bunch = Book.objects.none()
    action = request.POST.get("Action", '')

    # We need at least 1 thing to edit, otherwise bad things can happen
    if not request.POST.has_key('idToEdit1'):
        var_dict = {
            'message' : "Didn't get any books to process",
        }
        t = loader.get_template('400.html')
        c = RC(request, var_dict)
        return HttpResponseBadRequest(t.render(c))
    for key, value in request.POST.items():
        if "idToEdit" in key:
            bunch = bunch | Book.objects.filter(pk=int(value))
            
    if action == "Delete":
        bunch = bunch.exclude(status='D')
        for book in bunch:
            Log(action='D', book=book, who=request.user).save()
        var_dict = { 'num_deleted': bunch.count() }
        bunch.update(status='D')
        template = 'books/update_book/deleted.html'
        return rtr(template, var_dict, context_instance=RC(request))
    elif action[:1] == "To Be Deleted"[:1]:
        # apparently some browsers have issues passing spaces
        # can't do this for Deleted, Seller Paid, and Sold Books
        bunch = bunch.exclude(status__in='DPS')
        send_tbd_emails(bunch)
        for book in bunch:
            Log(action='T', book=book, who=request.user).save()
        var_dict = {
            'num_doomed' : bunch.count(),
            'num_owners' : len(set(map(lambda x: x.seller, bunch))),
        }
        bunch.update(status='T')
        template = 'books/update_book/to_be_deleted.html'
        return rtr(template, var_dict, context_instance=RC(request))
    elif action == "Sold":
        # Allow only if For Sale or On Hold
        bunch = bunch.filter(status__in='FO')
        for book in bunch:
            Log(action='S', book=book, who=request.user).save()
        send_sold_emails(list(bunch))
        var_dict = {
            'sold' : bunch.count(),
            'num_owners' : len(set(map(lambda x: x.seller, bunch))),
        }
        bunch.update(status='S', sell_date=datetime.today())
        template = 'books/update_book/sold.html'
        return rtr(template, var_dict, context_instance=RC(request))
    elif action[:5] == "Seller Paid"[:5]:
        # apparently some browsers have issues passing spaces
        # only staff can do this
        if not request.user.is_staff: bunch = Book.objects.none()
        # A Seller can be paid only after the book was sold
        else: bunch = bunch.filter(status='S')

        for book in bunch:
            Log(action='P', book=book, who=request.user).save()
        var_dict = {'paid' : bunch.count()}
        bunch.update(status='P')
        template = 'books/update_book/seller_paid.html'
        return rtr(template, var_dict, context_instance=RC(request))
    elif action == "Missing":
        # Must be For Sale, On Hold or To Be Deleted for it to go Missing
        bunch = bunch.filter(status__in='FOT')
        for book in bunch:
            Log(action='M', book=book, who=request.user).save()
        send_missing_emails(bunch)
        var_dict = {
            'num_owners' : len(set(map(lambda x: x.seller, bunch))),
            'num_missing' : bunch.count(),
        }
        bunch.update(status='M')
        template = 'books/update_book/missing.html'
        return rtr(template, var_dict,  context_instance=RC(request))
    elif action[:4] == "Place on Hold"[:4]:
        # apparently some browsers have issues passing spaces
        extended = bunch.filter(status='O', holder=request.user)
        new_hold = bunch.filter(status='F')
        failed = bunch.exclude(status__in='OF', holder=request.user)
        for book in new_hold:
            Log(action='O', book=book, who=request.user).save()
        for book in extended:
            Log(action='X', book=book, who=request.user).save()
        held = extended | new_hold
        var_dict = {
            'failed' : failed,
            'extended' : extended,
            'new_hold' : new_hold,
            'num_held' : held.count(),
            'total_price' : sum(map(lambda x: x.price, held)),
        }
        extended.update(hold_date = datetime.today())
        new_hold.update(status='O', hold_date=datetime.today(), holder=request.user)
        template = 'books/update_book/place_hold.html'
        return rtr(template, var_dict, context_instance=RC(request))
    elif action[:5] == "Remove Holds"[:5]:
        bunch = bunch.filter(status='O')
        if not request.user.is_staff: bunch = bunch.filter(holder=request.user)
        for book in bunch:
            Log(action='R', book=book, who=request.user).save()
        var_dict = {'removed' : bunch.count()}
        bunch.update(status='F', hold_date=None, holder=None)
        template = 'books/update_book/remove_holds.html'
        return rtr(template, var_dict, context_instance=RC(request))
    elif action == "Edit":
        if bunch.count() > 1: too_many = True
        else: too_many = False
        item = bunch[0]
        initial = {
            'seller' : item.seller.id,
            'price' : item.price,
            'barcode' : item.metabook.barcode,
        }
        form = BookForm(initial=initial)
        logs = Log.objects.filter(book=item)
        var_dict = {
            'form' : form,
            'too_many' : too_many,
            'id' : item.id,
            'logs' : logs,
        }
        template = 'books/update_book/edit.html'
        return rtr(template, var_dict, context_instance=RC(request))
    else:
        var_dict = {'action' : action}
        template = 'books/update_book/error.html'
        return rtr(template, var_dict, context_instance=RC(request))

@login_required()
def update_book_edit(request):
    """
    Applies changes to a book made on the edit page
    If the barcode doesn't exist,
    it makes the user create a MetaBook object as well
    
    Tests:
        - GETTest
        - SecurityTest
        - NotAllowedTest
    """
    if not request.method == "POST":
        t = loader.get_template('405.html')
        c = RC(request)
        return HttpResponseNotAllowed(t.render(c), ['POST'])
    # User must be staff or admin to get to this page
    if not request.user.is_staff:
        t = loader.get_template('403.html')
        c = RC(request)
        return HttpResponseForbidden(t.render(c))
    form = BookForm(request.POST)
    if form.is_valid():
        id_to_edit = request.POST.get('IdToEdit')
        try:
            book = Book.objects.get(id=id_to_edit)
        except Book.DoesNotExist:
            message = 'Book with ref# "%s" does not exist' % id_to_edit
            return tidy_error(request, message)
        try:
            barcode = form.cleaned_data['barcode']
            book.metabook = MetaBook.objects.get(barcode=barcode)
        except MetaBook.DoesNotExist:
            # barcode doesn't exist in db, we have to create a metabook.
            initial = {
                'barcode': barcode,
                'seller' : form.cleaned_data['seller'],
                'price' : form.cleaned_data['price'],
                'book_id' : book.id,
                'edition' : '1',
            }
            form = NewBookForm(initial=initial)
            var_dict = {'form' : form}
            template = 'books/attach_book.html'
            return rtr(template, var_dict, context_instance=RC(request))
        try:
            seller_id = form.cleaned_data['seller']
            book.seller = User.objects.get(id=seller_id)
        except User.DoesNotExist:
            user = import_user(seller_id)
            if user == None:
                message = "Invalid Student ID: %s" % id_to_edit
                return tidy_error(request, message)
            book.seller = user
        book.price = form.cleaned_data['price']
        book.save()
        Log(who=request.user, action='E', book=book).save()
        var_dict = {'book' : book}
        template = 'books/update_book/edited.html'
        return rtr(template, var_dict, context_instance=RC(request))
            
    elif request.POST.get('IdToEdit'):
        # form isn't valid, but we have an id to work with. send user back
        id_to_edit = request.POST.get('IdToEdit')
        var_dict = {
            'form' : form,
            'too_many' : False,
            'id' : id_to_edit,
            'logs' : Log.objects.filter(book=id_to_edit),
        }
        template = 'books/update_book/edit.html'
        return rtr(template, var_dict, context_instance=RC(request))

@login_required()
def attach_book(request):
    """
    Tests:
        - GETTest
        - SecurityTest
        - NotAllowedTest
    """
    # User must be staff or admin to get to this page
    if not request.user.is_staff:
        t = loader.get_template('403.html')
        c = RC(request)
        return HttpResponseForbidden(t.render(c))
    if not request.method == 'POST':
        t = loader.get_template('405.html')
        c = RC(request)
        return HttpResponseNotAllowed(t.render(c), ['POST'])
    form = NewBookForm(request.POST)
    if not form.is_valid():
        # The form has bad data. send the user back
        var_dict = {'form' : form}
        template = 'books/attach_book.html'
        return rtr(template, var_dict, context_instance=RC(request))
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

    book = Book.objects.get(pk=form.cleaned_data['book_id'])
    book.metabook = metabook
    book.save()
    var_dict = {'book' : book}
    template = 'books/attached.html'
    return rtr(template, var_dict, context_instance=RC(request))

@login_required()
def my_books(request):
    """
    Displays books the user has on hold
    and is selling, sorts by search box, filters, calculates total prices
    
    Tests: GETTest
    """
    #gets users books
    selling = Book.objects.filter(seller = request.user)  
    holding = Book.objects.filter(holder = request.user)    
    priceHold = 0
    priceSell = 0
    searched = False
    #calculate totals for book
    for book in holding:
        priceHold = book.price + priceHold         
    for book in selling:
        priceSell = book.price + priceSell
    
  
    # Filter for the search box
    if request.GET.has_key("filter") and request.GET.has_key("field"):
        # only run the filter if the GET args are there
        selling = book_filter(request.GET["filter"] , request.GET["field"],
                                  selling)
        holding = book_filter(request.GET["filter"] , request.GET["field"],
                                  holding)
        searched = True
    # Sorts results by request
    elif request.GET.has_key("sort_by") and request.GET.has_key("dir"):
        holding = book_sort(request.GET["sort_by"], request.GET["dir"])
        holding = holding.filter(holder = request.user)
    elif request.GET.has_key("sort_with") and request.GET.has_key("dir"):
        selling = book_sort(request.GET["sort_with"], request.GET["dir"])
        selling = selling.filter(seller = request.user)
   
    var_dict = {
         'sellP' : selling,
         'holdP' : holding,
         'priceH' : priceHold,
         'priceS' : priceSell,
         'field' : request.GET.get('field', 'any_field'),
         'filter_text' : request.GET.get('filter', ''),
         'search' : searched
    }             
    template = 'books/my_books.html'
    return rtr(template, var_dict, context_instance=RC(request))    
    
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
        var_dict = {
            'user_name' : user.get_full_name(),
            'administrator' : user.is_superuser,
        }
        template = 'books/update_staff/saved.html'
        return rtr(template, var_dict, context_instance=RC(request))

@login_required()
def add_book(request):
    """
    Tests:
        - GETTest
        - SecurityTest
    """
    # User must be staff or admin to get to this page
    if not request.user.is_staff:
        t = loader.get_template('403.html')
        c = RC(request)
        return HttpResponseForbidden(t.render(c))
    if request.method == "POST":
        form = BookForm(request.POST)
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
                    'price' : price,
                    'edition' : '1',
                }
                form = NewBookForm(initial=initial)
                var_dict = {'form' : form}
                template = 'books/add_new_book.html'
                return rtr(template, var_dict, context_instance=RC(request))
            try:
                seller = User.objects.get(id=student_id)
            except User.DoesNotExist:
                seller = import_user(student_id)
                if seller == None:
                    message = "Invalid Student ID: %s" % student_id
                    return tidy_error(request, message)
            book = Book(price=price, status="F", metabook=metabook, seller=seller)
            book.save()
            Log(book=book, who=request.user, action='A').save()
            var_dict = {
                'title' : metabook.title,
                'book_id' : book.id
            }
            template = 'books/update_book/added.html'
            return rtr(template, var_dict, context_instance=RC(request))
        # the form isn't valid. send the user back.
        var_dict = {'form' : form}
        template = 'books/add_book.html'
        return rtr(template, var_dict, context_instance=RC(request))
    else:
        # the user is hitting the page for the first time
        form = BookForm()
        var_dict = {'form' : form}
        template = 'books/add_book.html'
        return rtr(template, var_dict, context_instance=RC(request))

def add_new_book(request):
    """
    Tests:
        - GETTest
        - AddNewBookTest
        - SecurityTest
        - NotAllowedTest
    """
    if not request.method == 'POST':
        t = loader.get_template('405.html')
        c = RC(request)
        return HttpResponseNotAllowed(t.render(c), ['POST'])
    # User must be staff or admin to get to this page
    if not request.user.is_staff:
        t = loader.get_template('403.html')
        c = RC(request)
        return HttpResponseForbidden(t.render(c))
    if request.POST.get("Action", '') == 'Add':
        form = NewBookForm(request.POST)
        if form.is_valid():
            # This came from the add_book view, and we need to
            # create a book and a metabook
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
            book = Book(seller=seller, price=Decimal(price), metabook=metabook)
            book.status = 'F'
            book.save()
            Log(book=book, who=request.user, action='A').save()

            var_dict = {
                'title' : metabook.title,
                'author' : metabook.author,
                'seller_name' : seller.get_full_name(),
                'book_id' : book.id,
            }
            template = 'books/update_book/added.html'
            return rtr(template, var_dict, context_instance=RC(request))
        var_dict = {'form' : form}
        template = 'books/add_new_book.html'
        return rtr(template, var_dict, context_instance=RC(request))

@login_required()
def remove_holds_by_user(request):
    """
    Tests:
        - GETTest
        - SecurityTest
        - NotAllowedTest
    """
    if not request.method == "POST":
        t = loader.get_template('405.html')
        c = RC(request)
        return HttpResponseNotAllowed(t.render(c), ['POST'])
    # User must be staff or admin to get to this page
    if not request.user.is_staff:
        t = loader.get_template('403.html')
        c = RC(request)
        return HttpResponseForbidden(t.render(c))
    for key, value in request.POST.items():
        if "holder_id" == key:
            holder = User.objects.get(pk=int(value))
            break
    books = Book.objects.filter(holder=holder, status='O')
    for book in books:
        Log(action='R', book=book, who=request.user).save()
    var_dict = {'removed' : books.count()}
    books.update(status='F', hold_date=None, holder=None)
    template = 'books/update_book/remove_holds.html'
    return rtr(template, var_dict, context_instance=RC(request))
