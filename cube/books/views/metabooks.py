# Copyright (C) 2010  Trinity Western University

from cube.books.models import MetaBook, Course
from cube.books.forms import MetaBookForm, CourseForm
from cube.books.views.tools import metabook_sort, get_number
from cube.books.http import HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import HttpResponseForbidden
from django.shortcuts import render_to_response as rtr
from django.template import loader, RequestContext as RC

# pagination defaults
PER_PAGE = '30'
PAGE_NUM = '1'

@login_required()
def metabook_list(request):
    """
    List all metabooks in the database
    
    Tests:
        - GETTest
        - SecurityTest
    """
    # User must be staff or admin to get to this page
    if not request.user.is_staff:
        t = loader.get_template('403.html')
        c = RC(request)
        return HttpResponseForbidden(t.render(c))
    if request.GET.has_key("sort_by") and request.GET.has_key("dir"):
        metabooks = metabook_sort(request.GET["sort_by"], request.GET["dir"])
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
    var_dict = {
        'metabooks' : page_of_metabooks,
        'per_page' : metabooks_per_page,
        'page' : page_num,
        'dir' : 'desc' if request.GET.get('dir', '') == 'asc' else 'asc'
    }

    template = 'books/list_metabooks.html'
    return rtr(template, var_dict, context_instance=RC(request))

@login_required()
def update(request):
    """
    This view is used to update metabook data
    
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

    bunch = MetaBook.objects.none()
    action = request.POST.get("Action", '')
    for key, value in request.POST.items():
        if "idToEdit" in key:
            bunch = bunch | MetaBook.objects.filter(pk=int(value))
            
    if action == "Delete":
        bunch = bunch.exclude(status='D')
        var_dict = {'num_deleted': bunch.count()}
        bunch.update(status='D')
        template = 'books/update_book/deleted.html'
        return rtr(template, var_dict, context_instance=RC(request))
    elif action == "Edit":
        if bunch.count() > 1: too_many = True
        else: too_many = False
        item = bunch[0]
        metabook_form = MetaBookForm(instance=item)
        course = item.courses.all()[0]
        course_form = CourseForm(instance=course)
        var_dict = {
            'metabook_form' : metabook_form,
            'course_form' : course_form,
            'metabook_id' : item.id,
            'course_id' : course.id,
        }
        template = 'books/edit_metabook.html'
        return rtr(template, var_dict, context_instance=RC(request))
    elif action == "Save":
        metabook_id = request.POST.get('metabook_id', '')
        course_id = request.POST.get('course_id', '')
        metabook = MetaBook.objects.get(pk=metabook_id)
        course = Course.objects.get(pk=course_id)
        metabook_form = MetaBookForm(request.POST, instance=metabook)
        course_form = CourseForm(request.POST, instance=course)
        if metabook_form.is_valid() and course_form.is_valid():
            dept = course_form.cleaned_data['department']
            num = course_form.cleaned_data['number']
            tpl = Course.objects.get_or_create(department=dept, number=num)
            course = tpl[0]
            metabook = metabook_form.save()
            metabook.courses.add(course)

            var_dict={'metabook': metabook}
            template = 'books/update_metabook/saved.html'
            return rtr(template, var_dict, context_instance=RC(request))
        # the form isn't valid. send the user back
        var_dict = {
            'metabook_form' : metabook_form,
            'course_form' : course_form,
            # TODO need to check for metabook id before hitting here
            'metabook_id' : metabook_id,
        }
        template = 'books/edit_metabook.html'
        return rtr(template, var_dict, context_instance=RC(request))
    else:
        var_dict = {'action' : action}
        template = 'books/update_book/error.html'
        return rtr(template, var_dict, context_instance=RC(request))
