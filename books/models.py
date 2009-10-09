from django.db import models

class Book(models.Model):
    """
    Information on a book (as opposed to a particular copy of it)
    The attributes should be self-explanatory
    """
    title = models.CharField(max_length=250)
    author = models.CharField(max_length=70)
    barcode = models.CharField(max_length=50)
    edition = models.PositiveSmallIntegerField()
    add_date = models.DateTimeField('Date Added')

    def __unicode__(self):
        return self.title

class Course(models.Model):
    """
    Basic course data
    """
    #TODO NOTE: This model depends on how we end up grabbing course data
    code = models.CharField(max_length=5)
    number = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=250)

class Student(models.Model):
    """
    Stores info on the student/user
    the default id is used for the student number
    """
    # TODO this model will probably be replaced with django's User object
    first_name = models.CharField(max_length=35)
    last_name = models.CharField(max_length=35)
    email = models.EmailField()

    def __unicode__(self):
        return str(self.id)

    def name(self):
        return "%s %s" % (self.first_name, self.last_name)

class Listing(models.Model):
    """
    For when a student lists a particular copy of a book.
    Keeps track of 
        * when and who listed (is selling) it
        * if and who is currently holding it
        * when it was last put on hold
	* when it finally got sold
	* whether the listing is flagged for deletion or not
    """
    book = models.ForeignKey(Book)
    list_date = models.DateTimeField('Date Listed', auto_now_add=True)
    seller = models.ForeignKey(Student, related_name="selling")
    sell_date = models.DateTimeField('Date Sold', blank=True, null=True)
    holder = models.ForeignKey(Student, related_name="holding",
                               blank=True, null=True)
    hold_date = models.DateTimeField('Date Held', blank=True, null=True)
    doomed = models.BooleanField('Flagged for Deletion', default=False)
    price = models.DecimalField(max_digits=7, decimal_places=2)

    def __unicode__(self):
        return "%s by %s on %s" % (self.book, self.seller,
	                           self.list_date.date())
