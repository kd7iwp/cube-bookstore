# Copyright (C) 2010  Trinity Western University

from cube.users.forms import UserForm
from cube.books.http import HttpResponseNotAllowed

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response as rtr
from django.template import loader, RequestContext as RC
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

@login_required()
def profile(request):
    """
    Allow users to view their profile
    """
    if not request.method == "GET":
        t = loader.get_template('405.html')
        c = RC(request)
        return HttpResponseNotAllowed(t.render(c), ['GET'])
    template = 'users/profile.html'
    return rtr(template, {}, context_instance=RC(request))
    

@login_required()
def edit_profile(request):
    """
    Allows users to edit their own profile
    
    Tests:
       None yet
    """
    if request.method == 'GET':
        #Show the edit form
        form = UserForm({'email' : request.user.email})
        var_dict = { 'form' : form }
        template = 'users/edit_profile.html'
        return rtr(template, var_dict, context_instance=RC(request))
    elif request.method == 'POST':
        #Apply changes
        form = UserForm(request.POST)
        if form.is_valid():
            request.user.email = form.cleaned_data['email']
            request.user.save()
            return HttpResponseRedirect(reverse('cube.users.views.profile'))
        if not form.is_valid():
            # The form has bad data. send the user back
            var_dict = {'form' : form}
            template = 'users/edit_profile.html'
            return rtr(template, var_dict, context_instance=RC(request))

    

