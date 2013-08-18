# Copyright (C) 2010  Trinity Western University

from django import forms

class UserForm (forms.Form):
    email = forms.EmailField()
