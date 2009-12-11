from cube.settings import ADMINS as admin_emails
from django.core.mail import EmailMultiAlternatives
from django.template import loader, Context
import re

def strip_html(value):
    "Return the given HTML with all tags stripped."
    return re.sub(r'<[^>]*?>', '', value)

def send_missing_emails(listings):
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
        subj = 'Your book went missing at the Cube'
        #TODO using admin_email might not be the brightest idea
        frm = "The Cube <%s>" % admin_emails[0][1] 
        to = [owner.email]
        html_content = t.render(c)
        text_content = strip_html(html_content)
        msg = EmailMultiAlternatives(subj, text_content, frm, to)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
