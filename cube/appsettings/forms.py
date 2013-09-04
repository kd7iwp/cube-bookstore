# Copyright (C) 2010  Trinity Western University

from datetime import date

from cube.appsettings.models import AppSetting
from django import forms
from django.core.exceptions import ValidationError
from decimal import Decimal

class SettingForm(forms.Form):
    name = forms.CharField(max_length=200)
    value = forms.CharField(widget=forms.Textarea)
    description = forms.CharField(widget=forms.Textarea)
