# Copyright (C) 2010  Trinity Western University

from cube.books.models import Book, MetaBook, Course
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from django.core import mail

# test account details
PASSWORD = 'testpass'

# Test Administrator
ADMIN_USERNAME = 'test_admin'
ADMIN_EMAIL = 'admin@example.com'

# Test Staff
STAFF_USERNAME = 'test_staff'
STAFF_EMAIL = 'staff@example.com'

# Test User
TEST_USERNAME = 'test_user'
TEST_EMAIL = 'test@example.com'

class SimpleTest(TestCase):
    fixtures = ['test_empty.json']
    def setUp(self):
        self.client.login(username=ADMIN_USERNAME, password=PASSWORD)
    def test_book_list(self):
        """ Ensure Book List displays without errors """
        response = self.client.get('/books/')
        self.failUnlessEqual(response.status_code, 200)
    def test_my_books(self):
        """ Ensure My Books displays without errors """
        response = self.client.get('/my_books/')
        self.failUnlessEqual(response.status_code, 200)
    def test_add_book(self):
        """ Ensure Add Book page displays without errors """
        response = self.client.get('/add_book/')
        self.failUnlessEqual(response.status_code, 200)
    def test_list_metabooks(self):
        """ Ensure MetaBook list displays without errors """
        response = self.client.get('/metabooks/')
        self.failUnlessEqual(response.status_code, 200)
    def test_staff(self):
        """ Ensure Staff List displays without errors """
        response = self.client.get('/staff/')
        self.failUnlessEqual(response.status_code, 200)
    def test_update_staff(self):
        """ Ensure the staff update page returns HttpResponseNotAllowed """
        response = self.client.get('/update_staff/')
        self.failUnlessEqual(response.status_code, 405)
    def test_help(self):
        """ Ensure Help page displays without errors """
        response = self.client.get('/help/')
        self.failUnlessEqual(response.status_code, 200)
    def test_update_metabooks(self):
        """ Ensure the MetaBook update page displays without errors """
        response = self.client.get('/metabooks/update/')
        self.failUnlessEqual(response.status_code, 405)

from django.core import mail
class EmailTest(TestCase):
    fixtures = ['test_3_for_sale.json']
    def setUp(self):
        self.client.login(username=STAFF_USERNAME, password=PASSWORD)
    def test_send_mail(self):
        mail.send_mail('Subject', 'Message', 'from@cube.com',
                        ['to@example.com'], fail_silently=False)
        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, 'Subject')
    def test_sold(self):
        post_data = {
            'idToEdit1' : '1',
            'Action' : 'Sold',
        }
        response = self.client.post('/books/update/book/', post_data)
        self.assertEquals(len(mail.outbox), 1)
    def test_missing(self):
        post_data = {
            'idToEdit1' : '1',
            'Action' : 'Missing',
        }
        response = self.client.post('/books/update/book/', post_data)
        self.assertEquals(len(mail.outbox), 1)
    def test_tobodeleted(self):
        post_data = {
            'idToEdit1' : '1',
            'Action' : 'To Be Deleted',
        }
        response = self.client.post('/books/update/book/', post_data)
        self.assertEquals(len(mail.outbox), 1)



class AddNewBookTest(TestCase):
    fixtures = ['test_empty.json']
    def setUp(self):
        self.client.login(username=STAFF_USERNAME, password=PASSWORD)
    def test_feedback(self):
        """ Make sure feedback is correct when adding a new book """
        author = 'Bruce Wilkinson'
        title = 'The Prayer of Jabez'
        book_id = '1'
        post_data = {
            'barcode' : '9781590524756',
            'seller' : '3',
            'price' : '4.78',
            'author' : author,
            'title' : title,
            'edition' : '1',
            'department' : 'RELS',
            'course_number' : '123',
            'book_id' : book_id,
            'Action' : 'Add'
        }
        response = self.client.post('/add_new_book/', post_data)
        self.assertContains(response, author)
        self.assertContains(response, title)
        self.assertContains(response, '">%s</a>' % book_id)

class StaffTest(TestCase):
    fixtures = ['test_empty.json']
    def setUp(self):
        self.client.login(username=ADMIN_USERNAME, password=PASSWORD)
    def test_edit(self):
        post_data = {
            'idToEdit' : '1',
            'Action' : 'Edit',
        }
        response = self.client.post('/staff_edit/', post_data)
        self.assertContains(response, "Administrator")
    def test_add_page(self):
        """ Ensure the add staff page displays without errors """
        post_data = {
            'Action' : 'Add New',
        }
        response = self.client.post('/staff_edit/', post_data)
        self.failUnlessEqual(response.status_code, 200)
    # Commented out for 2 reasons
    # 1. It's a twupass dependent test
    # 2. It doesn't work, and I don't know why
    #def test_add(self):
    #    """ Ensure adding staff works """
    #    # This is a twupass dependent test
    #    post_data = {
    #        'student_id' : '194908',
    #        'role' : 'admin',
    #        'Action' : 'Save',
    #    }
    #    response = self.client.post('/update_staff/', post_data)
    #    self.failUnlessEqual(response.status_code, 200)
    #    self.assertContains(response, "Administrator")

class SearchBookTest(TestCase):
    fixtures = ['test_empty.json']
    TITLE = 'The Silmarillion'
    AUTHOR = 'J.R.R. Tolkien'
    BARCODE = '9780618391110'
    EDITION = 1
    def setUp(self):
        self.client.login(username=TEST_USERNAME, password=PASSWORD)
        self.get_data = {'field' : '', 'filter' : ''}

        self.course = Course(department='ENGL', number='103')
        self.course.save()

        metabook = MetaBook(title=self.TITLE, author=self.AUTHOR)
        metabook.barcode = self.BARCODE
        metabook.edition = self.EDITION
        metabook.save()
        metabook.courses.add(self.course)

        seller = User.objects.get(pk=3)

        self.book = Book(metabook=metabook, seller=seller)
        self.book.price = Decimal('1.01')
        self.book.save()

    # Barcode
    def test_barcode(self):
        """ Searching for barcodes in book list should work """
        self.get_data['field'] = 'barcode'
        self.get_data['filter'] = self.BARCODE
        response = self.client.get('/books/', self.get_data)
        self.assertContains(response, self.TITLE)
    def test_barcode_anyfield(self):
        """ Searching for barcodes in any field """
        self.get_data['field'] = 'any_field'
        self.get_data['filter'] = self.BARCODE
        response = self.client.get('/books/', self.get_data)
        self.assertContains(response, self.TITLE) 
    # Title
    def test_title(self):
        """ Searching for title """
        self.get_data['field'] = 'title'
        self.get_data['filter'] = self.TITLE
        response = self.client.get('/books/', self.get_data)
        self.assertContains(response, self.AUTHOR)
    def test_title_anyfield(self):
        """ Searching for title in any field """
        self.get_data['field'] = 'any_field'
        self.get_data['filter'] = self.TITLE
        response = self.client.get('/books/', self.get_data)
        self.assertContains(response, self.AUTHOR)
    # Author
    def test_author(self):
        """ Searching for author """
        self.get_data['field'] = 'author'
        self.get_data['filter'] = self.AUTHOR
        response = self.client.get('/books/', self.get_data)
        self.assertContains(response, self.TITLE)
    def test_author_anyfield(self):
        """ Searching for author in Any Field """
        self.get_data['field'] = 'any_field'
        self.get_data['filter'] = self.AUTHOR
        response = self.client.get('/books/', self.get_data)
        self.assertContains(response, self.TITLE)
    # Course Code
    def test_course_code(self):
        """ Searching for course code """
        self.get_data['field'] = 'course_code'
        self.get_data['filter'] = self.course.code()
        response = self.client.get('/books/', self.get_data)
        self.assertContains(response, self.AUTHOR)
    def test_course_code_anyfield(self):
        """ Searching for course code in any field """
        self.get_data['field'] = 'any_field'
        self.get_data['filter'] = self.course.code()
        response = self.client.get('/books/', self.get_data)
        self.assertContains(response, self.AUTHOR)
    # Ref #
    def test_refno(self):
        """ Searching for course code """
        self.get_data['field'] = 'ref_no'
        self.get_data['filter'] = self.EDITION
        response = self.client.get('/books/', self.get_data)
        self.assertContains(response, self.AUTHOR)
    def test_refno_anyfield(self):
        """ Searching for course code in any field """
        self.get_data['field'] = 'any_field'
        self.get_data['filter'] = self.EDITION
        response = self.client.get('/books/', self.get_data)
        self.assertContains(response, self.AUTHOR)

#TODO implement this
#class SearchBookStatusTest(TestCase):
#    """
#    Searching Status gets its own test class because
#    it's a little more complicated than the others
#    """
#    def setUp(self):
#        self.client.login(username='test_user', password=PASSWORD)
#        self.get_data = {'field' : 'status', 'filter' : ''}
#    def test_forsale(self):
#        self.get_data['filter'] = 'For Sale'
        
class SortBookTest(TestCase):
    fixtures = ['test_empty.json']
    def setUp(self):
        self.client.login(username=ADMIN_USERNAME, password=PASSWORD)
    def test_title_asc(self):
        """ Make sure sorting books by title in ascending order works"""
        get_data = {
            'sort_by' : 'metabook__title',
            'dir' : 'asc',
        }
        response = self.client.get('/books/', get_data)
        self.failUnlessEqual(response.status_code, 200)
    def test_title_desc(self):
        """ Make sure sorting books by title in descending order works"""
        get_data = {
            'sort_by' : 'metabook__title',
            'dir' : 'desc',
        }
        response = self.client.get('/books/', get_data)
        self.failUnlessEqual(response.status_code, 200)
    def test_author_asc(self):
        """ Make sure sorting books by author in ascending order works"""
        get_data = {
            'sort_by' : 'metabook__author',
            'dir' : 'asc',
        }
        response = self.client.get('/books/', get_data)
        self.failUnlessEqual(response.status_code, 200)
    def test_author_desc(self):
        """ Make sure sorting books by author in descending order works"""
        get_data = {
            'sort_by' : 'metabook__author',
            'dir' : 'desc',
        }
        response = self.client.get('/books/', get_data)
        self.failUnlessEqual(response.status_code, 200)
    def test_price_asc(self):
        """ Make sure sorting books by price in ascending order works"""
        get_data = {
            'sort_by' : 'price',
            'dir' : 'asc',
        }
        response = self.client.get('/books/', get_data)
        self.failUnlessEqual(response.status_code, 200)
    def test_price_desc(self):
        """ Make sure sorting books by price in descending order works"""
        get_data = {
            'sort_by' : 'price',
            'dir' : 'desc',
        }
        response = self.client.get('/books/', get_data)
        self.failUnlessEqual(response.status_code, 200)
    def test_courses_asc(self):
        """ Make sure sorting books by courses in ascending order works"""
        get_data = {
            'sort_by' : 'metabook__courses',
            'dir' : 'asc',
        }
        response = self.client.get('/books/', get_data)
        self.failUnlessEqual(response.status_code, 200)
    def test_courses_desc(self):
        """ Make sure sorting books by courses in descending order works"""
        get_data = {
            'sort_by' : 'metabook__courses',
            'dir' : 'desc',
        }
        response = self.client.get('/books/', get_data)
        self.failUnlessEqual(response.status_code, 200)

class SecurityTest(TestCase):
    fixtures = ['test_empty.json']
    def setUp(self):
        self.client.login(username=TEST_USERNAME, password=PASSWORD)
    def test_staff_edit(self):
        """ Make sure normal users can't get to the staff edit page """
        response = self.client.get('/staff_edit/')
        self.failUnlessEqual(response.status_code, 403)
