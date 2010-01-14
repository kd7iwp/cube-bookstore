from cube.settings import ADMINS as admin_emails
from cube.books.models import Listing
from django.core.mail import EmailMultiAlternatives
from django.template import loader, Context
from re import sub

def strip_html(value):
    "Return the given HTML with all tags stripped."
    return sub(r'<[^>]*?>', '', value)

def index_by_owner(listings):
    items = {}
    for listing in listings:
        if items.has_key(listing.seller):
            items[listing.seller].append(listing)
        else:
            items[listing.seller] = [listing]
    return items

def create_context(owner, listings):
    return Context({
        'name' : owner.first_name,
        'num_listings' : len(listings),
        'book_titles' : map(lambda x: x.metabook.title, listings),
        'owner_selling' : Listing.objects.filter(seller=owner, status='F'),
        'admin_email' : admin_emails[0][1],
    })

def create_email(subj, html_content, owner_email):
    #TODO using admin_email might not be the brightest idea
    frm = "The Cube <%s>" % admin_emails[0][1]
    to = [owner_email]
    text_content = strip_html(html_content)
    msg = EmailMultiAlternatives(subj, text_content, frm, to)
    msg.attach_alternative(html_content, "text/html")
    return msg

def send_missing_emails(listings):
    t = loader.get_template('email/missing.html')
    missing = index_by_owner(listings)
    for owner, listings in missing.items():
        c = create_context(owner, listings)
        if len(listings) == 1: p = ''
        else: p = 's'
        subj = 'Your book%s went missing at the Cube' % p
        msg = create_email(subj, t.render(c), owner.email)
        msg.send()

def send_sold_emails(listings):
    t = loader.get_template('email/sold.html')
    sold = index_by_owner(listings)
    for owner, listings in sold.items():
        c = create_context(owner, listings)
        if len(listings) == 1: p = ' has'
        else: p = 's have'
        subj = 'Your book%s been sold at the Cube' % p
        msg = create_email(subj, t.render(c), owner.email)
        msg.send()

def send_tbd_emails(listings):
    t = loader.get_template('email/to_be_deleted.html')
    to_be_deleted = index_by_owner(listings)
    for owner, listings in to_be_deleted.items():
        c = create_context(owner, listings)
        if len(listings) == 1: p = ' was'
        else: p = 's were'
        subj = 'Your book%s not sold at the Cube' % p
        msg = create_email(subj, t.render(c), owner.email)
        msg.send()
