# Copyright (C) 2010  Trinity Western University

# django imports
from cube.appsettings.models import AppSetting
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
def setting_list(request):
    """
    Shows a list of all the application settings.
    Does pagination, sorting and filtering.
    
    Tests:
    """
    house_cleaning()
    # Filter for the search box
    if request.method == 'GET':
        filter_form = FilterForm(request.GET)
        if filter_form.is_valid():
            cd = filter_form.cleaned_data
            all_settings = AppSetting.objects.all()
            settings = settings_filter(cd['filter'], cd['field'], all_settings)
        elif request.GET.has_key("sort_by") and request.GET.has_key("dir"):
            settings = setting_sort(request.GET["sort_by"], request.GET["dir"])
        else:
            settings = AppSetting.objects.all()

# This filter for permissions was copied from the books view but probably isn't needed here
    # Filter according to permissions
#    if not request.user.is_staff:
        # Non staff can only see books which are for sale.
#        books = filter(lambda x: x.status == 'F', books)

    # Pagination
    page_num = get_number(request.GET, 'page', PAGE_NUM)
    settings_per_page = get_number(request.GET, 'per_page', PER_PAGE)

    paginator = Paginator(settings, settings_per_page)
    try:
        page_of_settings = paginator.page(page_num)
    except (EmptyPage, InvalidPage):
        page_of_settings = paginator.page(paginator.num_pages)

    # Template time
    if request.GET.get('dir', '') == 'asc': dir = 'desc'
    else: dir = 'asc'
    var_dict = {
        'appsettings' : page_of_settings,
        'per_page' : settings_per_page,
        'page' : page_num,
        'field' : request.GET.get('field', 'any_field'),
        'filter_text' : request.GET.get('filter', ''),
        'dir' : dir
    }
    return rtr('appsettings/settings_list.html', var_dict, context_instance=RC(request))

@login_required()
def edit_setting(request):
    """
    This view is used to update the values for an Application Setting
    
    Tests:
    """
    if not request.method == "POST":
        t = loader.get_template('405.html')
        c = RC(request)
        return HttpResponseNotAllowed(t.render(c), ['POST'])
    action = request.POST.get("Action", '')

    # We need at least 1 thing to edit, otherwise bad things can happen
    if not request.POST.has_key('idToEdit1'):
        var_dict = {
            'message' : "Didn't get any settings to process",
        }
        t = loader.get_template('400.html')
        c = RC(request, var_dict)
        return HttpResponseBadRequest(t.render(c))
    else: 
        specified_id = request.POST['idToEdit1']
        item = get_object_or_404(AppSetting, pk=int(specified_id))
    
        var_dict = {
            'name' : item.name,
            'value' : item.value,
            'description' : item.description,
            'too_many' : too_many,
            'id' : item.id,
            'logs' : logs,
        }
        template = 'appsettings/update/edit.html'
        return rtr(template, var_dict, context_instance=RC(request))

@login_required()
def save_setting_edit(request):
    """
    Applies changes to an AppSetting on the edit page
    
    Tests:
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
            setting = AppSetting.objects.get(id=id_to_edit)
        except AppSetting.DoesNotExist:
            message = 'Application Setting with ref# "%s" does not exist' % id_to_edit
            return tidy_error(request, message)
    elif request.POST.get('IdToEdit'):
        # form isn't valid, but we have an id to work with. send user back
        id_to_edit = request.POST.get('IdToEdit')
        var_dict = {
            'form' : form,
            'too_many' : False,
            'id' : id_to_edit,
            'logs' : Log.objects.filter(setting=id_to_edit),
        }
# Need the URL for the setting edit page        
        template = 'appsettings/setting_edit.html'
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
