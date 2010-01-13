from django.test import TestCase

class SimpleTest(TestCase):
    fixtures = ['test_empty.json']
    def setUp(self):
        self.client.login(username='test_admin', password='testpass')
    def test_listing_list(self):
        response = self.client.get('/books/')
        self.failUnlessEqual(response.status_code, 200)
    def test_my_books(self):
        response = self.client.get('/my_books/')
        self.failUnlessEqual(response.status_code, 200)
    def test_add_listing(self):
        response = self.client.get('/add_listing/')
        self.failUnlessEqual(response.status_code, 200)
    def test_list_books(self):
        response = self.client.get('/list_books/')
        self.failUnlessEqual(response.status_code, 200)
    def test_staff(self):
        response = self.client.get('/staff/')
        self.failUnlessEqual(response.status_code, 200)
    def test_help(self):
        response = self.client.get('/help/')
        self.failUnlessEqual(response.status_code, 200)
    def test_update_books(self):
        response = self.client.get('/books/update/book/')
        self.failUnlessEqual(response.status_code, 405)
