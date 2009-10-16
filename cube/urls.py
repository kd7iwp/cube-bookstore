from cube.books.models import Listing
from django.contrib import admin
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.views.generic.list_detail import object_list

admin.autodiscover()

list_args = {
    'queryset' : Listing.objects.all(),
}
# TODO add paginate_by

urlpatterns = patterns('',
    url(r'^$', object_list, list_args, name="list"),
    (r'^help/', direct_to_template, {'template' : 'help.html'}),

    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/(.*)', admin.site.root),
)
