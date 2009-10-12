from cube.books.models import Listing
from django.shortcuts import render_to_response

def list(request):
    listings = Listing.objects.all()
    return render_to_response('books/list.html', {'listings': listings})
