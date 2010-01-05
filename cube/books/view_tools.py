from cube.books.models import Listing
from django.db.models.query import QuerySet


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
                q = q & f(book__courses__division__icontains=word)
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
