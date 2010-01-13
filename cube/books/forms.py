from cube.books.models import Book, Course, Listing, DEPARTMENT_CHOICES
from django import forms
from django.core.exceptions import ValidationError
from decimal import Decimal

class CourseNumberField(forms.IntegerField):
    # TODO this doesn't seem to be working
    def validate(value):
        if len(str(value)) < 2:
            raise ValidationError("The Course Number %d is too short" % value)
        if len(str(value)) > 3:
            raise ValidationError("The Course Number %d is too long" % value)

class BookAndListingForm(forms.Form):
    barcode = forms.CharField(max_length=50)
    seller = forms.IntegerField(label="Student ID", min_value=1)
    price = forms.DecimalField(min_value=Decimal("1"), max_digits=7,
                               decimal_places=2)
    author = forms.CharField(max_length=70)
    title = forms.CharField(max_length=250)
    edition = forms.IntegerField(min_value=1)
    department = forms.ChoiceField(choices=DEPARTMENT_CHOICES)
    course_number = CourseNumberField()

    listing_id = forms.IntegerField(required=False, widget=forms.HiddenInput())

    def clean_barcode(self):
        return self.cleaned_data['barcode'].replace('-', '')

class BookForm(forms.ModelForm):
    class Meta:
        model = Book

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course

class ListingForm(forms.Form):
    seller = forms.IntegerField(label="Student ID", min_value=1)
    price = forms.DecimalField(min_value=Decimal("1"), max_digits=7,
                               decimal_places=2)
    barcode = forms.CharField(max_length=50)

class FilterForm(forms.Form):
    """
    Used for searching for books on the main page
    """
    FILTER_CHOICES = (
        ('any_field', 'In Any Field'),
        ('title', 'Title'),
        ('author', 'Author'),
        ('course_code', 'Course Code'),
        ('ref', 'Ref #'),
        ('status', 'Status'),
    )
    filter = forms.CharField()
    field = forms.ChoiceField(choices=FILTER_CHOICES)

