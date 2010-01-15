from django.test import TestCase

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
        response = self.client.get('/books/')
        self.failUnlessEqual(response.status_code, 200)
    def test_my_books(self):
        response = self.client.get('/my_books/')
        self.failUnlessEqual(response.status_code, 200)
    def test_add_book(self):
        response = self.client.get('/add_book/')
        self.failUnlessEqual(response.status_code, 200)
    def test_list_metabooks(self):
        response = self.client.get('/list_metabooks/')
        self.failUnlessEqual(response.status_code, 200)
    def test_staff(self):
        response = self.client.get('/staff/')
        self.failUnlessEqual(response.status_code, 200)
    def test_help(self):
        response = self.client.get('/help/')
        self.failUnlessEqual(response.status_code, 200)
    def test_update_metabooks(self):
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
