# Copyright (C) 2010  Trinity Western University

from cube.settings import ADMINS as admin_emails
from cube.books.models import Book
from django.core.mail import EmailMultiAlternatives
from django.template import loader, Context
from re import sub

def strip_html(value):
    "Return the given HTML with all tags stripped."
    return sub(r'<[^>]*?>', '', value)

def index_by_owner(books):
    items = {}
    for book in books:
        if items.has_key(book.seller):
            items[book.seller].append(book)
        else:
            items[book.seller] = [book]
    return items

def create_context(owner, books):
    return Context({
        'name' : owner.first_name,
        'num_books' : len(books),
        'book_titles' : map(lambda x: x.metabook.title, books),
        'owner_selling' : Book.objects.filter(seller=owner, status='F'),
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

def send_missing_emails(books):
    t = loader.get_template('email/missing.html')
    missing = index_by_owner(books)
    for owner, books in missing.items():
        c = create_context(owner, books)
        if len(books) == 1: p = ''
        else: p = 's'
        subj = 'Your book%s went missing at the Cube' % p
        msg = create_email(subj, t.render(c), owner.email)
        msg.send()

def send_sold_emails(books):
    t = loader.get_template('email/sold.html')
    sold = index_by_owner(books)
    for owner, books in sold.items():
        c = create_context(owner, books)
        if len(books) == 1: p = ' has'
        else: p = 's have'
        subj = 'Your book%s been sold at the Cube' % p
        msg = create_email(subj, t.render(c), owner.email)
        msg.send()

def send_tbd_emails(books):
    t = loader.get_template('email/to_be_deleted.html')
    to_be_deleted = index_by_owner(books)
    for owner, books in to_be_deleted.items():
        c = create_context(owner, books)
        if len(books) == 1: p = ' was'
        else: p = 's were'
        subj = 'Your book%s not sold at the Cube' % p
        msg = create_email(subj, t.render(c), owner.email)
        msg.send()
