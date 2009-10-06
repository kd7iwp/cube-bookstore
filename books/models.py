from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=250)
    author = models.CharField(max_length=100)
    barcode = models.CharField(max_length=50)
    edition = models.IntegerField()
    add_date = models.DateTimeField('Date Added')
    # Should we have a course table? 
    # TODO check to see how the old cube does courses

class Student(models.Model):
    number = models.CharField(max_length=10)

class Listing(models.Model):
    book = models.ForeignKey(Book)
    list_date = models.DateTimeField('Date Listed')
    seller = models.ForeignKey(Student, related_name="sell_item")
    sell_date = models.DateTimeField('Date Sold')
    holder = models.ForeignKey(Student, related_name="purchase_item")
    hold_date = models.DateTimeField('Date Held')
    price = models.DecimalField(max_digits=7, decimal_places=2)
