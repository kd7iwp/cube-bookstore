from django.db import models

class Course(models.Model):
    """
    Basic course data
    """
    #TODO NOTE: This model depends on how we end up grabbing course data
    division = models.CharField(max_length=5)
    number = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=250)

    def code(self):
        return "%s %s" % (self.division, self.number)

    def __unicode__(self):
        return self.code()

class Book(models.Model):
    """
    Information on a book (as opposed to a particular copy of it)
    The attributes should be self-explanatory
    """
    title = models.CharField(max_length=250)
    author = models.CharField(max_length=70)
    barcode = models.CharField(max_length=50)
    edition = models.PositiveSmallIntegerField()
    courses = models.ManyToManyField(Course)

    def __unicode__(self):
        return self.title

    def course_codes(self):
        """
        returns a list of courses in the form
        course1, course2, course3
        """
        course_list = ""
        for course in self.courses.all():
            course_list += "%s, " % course.code()
        # [:-2] takes off the trailing comma and space
        return course_list[:-2]

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
        return self.name()

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
    STATUS_CHOICES = (
        (u'F', u'For Sale'),
        (u'M', u'Missing'),
        (u'O', u'On Hold'),
        (u'P', u'Seller Paid'),
        (u'S', u'Sold'),
    )

    book = models.ForeignKey(Book)
    list_date = models.DateTimeField('Date Listed', auto_now_add=True)
    seller = models.ForeignKey(Student, related_name="selling")
    sell_date = models.DateTimeField('Date Sold', blank=True, null=True)
    holder = models.ForeignKey(Student, related_name="holding",
                               blank=True, null=True)
    hold_date = models.DateTimeField('Date Held', blank=True, null=True)
    doomed = models.BooleanField('Flagged for Deletion', default=False)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)

    def __unicode__(self):
        return "%s by %s on %s" % (self.book, self.seller,
	                           self.list_date.date())
