# Copyright (C) 2010  Trinity Western University

from cube.books.models import MetaBook
from xml.dom import minidom
import urllib

KEY = "TSQ5UZ6Y"
ISBNDB_URL = "http://isbndb.com/api/books.xml?access_key=%s&index1=isbn&value1=%s"

class ISBNException(Exception):
    def __init__(self, value):
        self.parameter = value

    def __str__(self):
        return repr(self.parameter)

def get_text(elements):
    nodelist = elements[0].childNodes
    rc = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
    return rc

def get_book(isbn):
    url = ISBNDB_URL % (KEY, isbn)
    dom = minidom.parse(urllib.urlopen(url))
    get = dom.getElementsByTagName
    errors = get("ErrorMessage")
    if errors: raise ISBNException(get_text(errors))
    titles = get("Title")
    authors = get("AuthorsText")
    if not (titles and authors): raise ISBNException("Book not found")
    metabook = MetaBook()
    metabook.title = get_text(titles)
    metabook.author = get_text(authors)
    return metabook
