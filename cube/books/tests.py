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
