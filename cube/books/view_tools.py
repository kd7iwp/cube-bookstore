from cube.books.models import Listing, Book
from cube.twupass.backend import TWUPassBackend
from cube.books.email import send_tbd_emails
from django.db.models.query import QuerySet
from datetime import datetime, timedelta
from django.shortcuts import render_to_response
from django.template import RequestContext

def expire_holds():
    """
    Expires holds on books after 24 hours
    """
    yester = datetime.today() - timedelta(1)
    expired_listings = Listing.objects.filter(status='O', hold_date__lte=yester)
    expired_listings.update(status='F', holder=None, hold_date=None)

def warn_annual_sellers():
    """
    If a listing is a year old, mark it as to be deleted and send them an email
    """
    last_year = datetime.today() - timedelta(365)
    old_listings = Listing.objects.filter(status='F', list_date__lte=last_year)
    send_tbd_emails(old_listings)
    old_listings.update(status='T')

def house_cleaning():
    """
    calls methods which need to be done frequently
    """
    expire_holds()
    warn_annual_sellers()

def tidy_error(request, error_message):
    """
    takes a request and an error message and returns a
    tidy HttpResponse with it
    """
    return render_to_response('error.html', {'message' : error_message },
                              context_instance=RequestContext(request))
def import_user(id):
    """
    Gets imports a user from twupass and returns it
    """
    return TWUPassBackend().import_user(id)

def get_number(list, key, default):
    """
    grabs a string from a list and converts it to a number
    if it can't, then it returns the integer conversion of default
    which is assumed to work
    """
    try:
        number = int(list.get(key, default))
    except ValueError:
        number = int(default)
    return number

def listing_filter(filter, field, listings):
    """
    Returns a filtered list of Listing objects only if the field is valid
    otherwise it returns all of the listing objects
    """
    def status(filter):
        for choice in Listing.STATUS_CHOICES:
            if filter.lower() in choice[1].lower():
                return listings.filter(status=choice[0])
        return Listing.objects.none()

    def course(filter):
        q = listings
        f = listings.filter
        for word in filter.split():
            try:
                x = int(word)
                q = q & f(book__courses__number__icontains=word)
            except ValueError:
                q = q & f(book__courses__department__icontains=word)
        return q.distinct()

    def ref(filter):
        try:
            return listings.filter(pk=int(filter))
        except ValueError:
            return Listing.objects.none()

    def title(filter):
        return listings.filter(book__title__icontains=filter)

    def author(filter):
        return listings.filter(book__author__icontains=filter)

    if field == "any_field":
        # do all the queries and merge them with the | operator
        # all queries being |'d must be either distinct or non-distinct
        return author(filter).distinct() |\
               author(filter).distinct() |\
               course(filter).distinct() |\
               ref(filter).distinct() |\
               status(filter).distinct()
    elif field == "title":
        return title(filter)
    elif field == "author":
        return author(filter)
    elif field == "course_code":
        return course(filter)
    elif field == "ref":
        return ref(filter)
    elif field == "status":
        return status(filter)
    else:
        return listings

def listing_sort(field, dir):
    dir = '-' if dir == 'desc' else ''
    return Listing.objects.order_by("%s%s" % (dir, field))

def book_sort(field, dir):
    dir = '-' if dir == 'desc' else ''
    return Book.objects.order_by("%s%s" % (dir, field))
