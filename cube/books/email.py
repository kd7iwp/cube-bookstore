from cube.settings import ADMINS as admin_emails
from django.core.mail import send_mail
from django.template import loader, Context

def send_missing_emails(listings):
    email = admin_emails[0][1] #TODO this might not be the brightest idea
    t = loader.get_template('email/missing.html')
    missing = {}
    for listing in listings:
        if missing.has_key(listing.seller):
            missing[listing.seller].append(listing)
        else:
            missing[listing.seller] = [listing]
    for owner, listings in missing.items():
        c = Context({
            'name' : owner.first_name,
            'num_listings' : len(listings),
            'book_titles' : map(lambda x: x.book.title, listings),
        })
        send_mail('Your book went missing at The Cube', t.render(c), email,
                  [owner.email])
