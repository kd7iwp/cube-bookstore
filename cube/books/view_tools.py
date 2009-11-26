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

def listing_filter(filter, field):
    """
    Returns a filtered list of Listing objects only if the field is valid
    otherwise it returns all of the listing objects
    """
    def status(filter):
        for choice in Listing.STATUS_CHOICES:
            if filter in choice[1]:
                return Listing.objects.filter(status=choice[0])
        return Listing.objects.none()

    def course(filter):
        q = Listing.objects.all()
        f = Listing.objects.filter
        for word in filter.split():
            try:
                x = int(word)
                q = q & f(book__courses__number__icontains=word)
            except ValueError:
                q = q & f(book__courses__division__icontains=word)
        return q

    def ref(filter):
        try:
            return Listing.objects.filter(pk=int(filter))
        except ValueError:
            return Listing.objects.none()

    def title(filter):
        return Listing.objects.filter(book__title__icontains=filter)

    def author(filter):
        return Listing.objects.filter(book__author__icontains=filter)

    if field == "any_field":
        # do all the queries and merge them with the | operator
        return author(filter) |\
               author(filter) |\
               course(filter) |\
               ref(filter) |\
               status(filter)
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
        return Listing.objects.all()
