from cube.books.models import Book, MetaBook, Course
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User

# test account details
PASSWORD = 'testpass'

# Test Administrator
ADMIN_USERNAME = 'test_admin'
ADMIN_EMAIL = 'admin@example.com'

# Test Staff
STAFF_USERNAME = 'test_staff'
STAFF_EMAIL = 'staff@example.com'

# Test User
TEST_USERNAME = 'test'
TEST_EMAIL = 'test@example.com'

class SimpleTest(TestCase):
    fixtures = ['test_empty.json']
    def setUp(self):
        self.client.login(username='test_admin', password='testpass')
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
        """ Ensure MetaBook List displays without errors """
        response = self.client.get('/list_metabooks/')
        self.failUnlessEqual(response.status_code, 200)
    def test_staff(self):
        """ Ensure Staff List displays without errors """
        response = self.client.get('/staff/')
        self.failUnlessEqual(response.status_code, 200)
    def test_help(self):
        """ Ensure Help page displays without errors """
        response = self.client.get('/help/')
        self.failUnlessEqual(response.status_code, 200)
    def test_update_metabooks(self):
        """ Ensure the MetaBook update page displays without errors """
        response = self.client.get('/books/update/metabook/')
        self.failUnlessEqual(response.status_code, 405)

#from django.core import mail
#class EmailTest(TestCase):
#    def test_sold(self):
#        mail.send_mail('

class AddNewBookTest(TestCase):
    fixtures = ['test_empty.json']
    def setUp(self):
        self.client.login(username='test_staff', password='testpass')
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
        self.assertContains(response, 'reference # %s' % book_id)

class SeachBookTest(TestCase):
    fixtures = ['test_empty.json']
    TITLE = 'The Silmarillion'
    AUTHOR = 'J.R.R. Tolkien'
    BARCODE = '9780618391110'
    EDITION = 1
    def setUp(self):
        self.client.login(username='test_user', password='testpass')
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
#        self.client.login(username='test_user', password='testpass')
#        self.get_data = {'field' : 'status', 'filter' : ''}
#    def test_forsale(self):
#        self.get_data['filter'] = 'For Sale'
        
