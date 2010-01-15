from django.contrib.auth.models import User
from cube.books.views.tools import get_number
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response as rtr
from django.template import RequestContext as RC

# pagination defaults
PAGE_NUM = '1'
PER_PAGE = '20'

@login_required()    
def staff_list(request):
    users = User.objects.filter(is_staff = True)
    page_num = get_number(request.GET, 'page', PAGE_NUM)
    users_per_page = get_number(request.GET, 'per_page', PER_PAGE)
    paginator = Paginator(users, users_per_page)
    try:
        page_of_users = paginator.page(page_num)
    except (EmptyPage, InvalidPage):
        page_of_users = paginator.page(paginator.num_pages)
    if request.GET.get('dir', '') == 'asc': dir = 'desc'
    else: dir = 'asc'
    vars = {
        'users' : page_of_users,
        'per_page' : users_per_page,
        'page' : page_num,
        'field' : request.GET.get('field', 'any_field'),
        'filter_text' : request.GET.get('filter', ''),
        'dir' : dir, 
    }
    template = 'books/staff.html'
    return rtr(template, vars,  context_instance=RC(request))

@login_required()
def update_staff(request):
    if request.method == 'POST':
        student_id = request.POST.get("student_id", '')
        action = request.POST.get('Action')
    else:
        return HttpResponseNotAllowed(['POST'])
    # Delete User
    if action == "Delete" and student_id:
        # Delete single
        try:
            user = User.objects.get(id = student_id)
            user.is_superuser = False
            user.is_staff = False
            user.save()
            vars = { 'num_deleted' : 1 }
            template = 'books/update_staff/deleted.html'
            return rtr(template, vars,  context_instance=RC(request))
        except User.DoesNotExist:
            return tidy_error(request, "Invalid Student ID: %s" % student_id)
    elif action == "Delete":
        # Delete multiple
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
            template = 'books/update_staff/deleted.html'
            return rtr(template, vars,  context_instance=RC(request))
        except User.DoesNotExist:
            if num_deleted == 1: p = ' was'
            else: p = 's were'
            message = "Only %d user%s" % (num_deleted, p) + \
                      "deleted because %s is an invalid student ID" % value
            return tidy_error(request, message) 

@login_required()
def staffedit(request):
    """
    Displays an edit page for user permissions
    If the data needs to be updated (e.g. delete or save)
    then it passes the request on to update_staff
    """
    if request.method == "POST":
        users = []
        too_many = False
        if request.POST.get('Action', '') == "Delete":
            return update_staff(request)
        users = []
        if request.POST.get('Action', '') == "Edit":
            edit = True
            for key, value in request.POST.items():
                if "idToEdit" in key:
                    users.append(User.objects.get(id=value))
            if len(users) > 1: too_many = True
            if len(users) == 0:
                # They clicked edit without selecting any users. How silly.
                return staff_list(request)
        else:
            users.append(User())
    else:
        too_many = False
        users = [User()]
        edit = False
    vars = {
        'edit' : edit,
        'too_many' : too_many,
        'name' : users[0].get_full_name(),
        'student_id' : users[0].id,
        'current_role' : 'admin' if users[0].is_superuser else 'staff' 
    }
    template = 'books/staffedit.html'
    return rtr(template, vars, context_instance=RC(request))


