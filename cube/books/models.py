# Copyright (C) 2010  Trinity Western University

from django.db import models
from django.contrib.auth.models import User

DEPARTMENT_CHOICES = (
    ('ALDR', 'MA Leadership'),
    ('ANTH', 'Anthropology'),
    ('ART', 'Art'),
    ('AV', 'Aviation'),
    ('AVIA', 'Aviation'),
    ('BIC', 'Bible Exposition'),
    ('BIE', 'Bible Exposition'),
    ('BIL', 'Biblical Languages'),
    ('BIOL', 'Biology'),
    ('BOTA', 'Biology'),
    ('BUSI', 'Business'),
    ('CAP', 'Contemporary Apologetics'),
    ('CARR', 'Career Skills Courses'),
    ('CATH', 'Catholicism'),
    ('CCM', 'Cross Cultural Ministries'),
    ('CEC', 'Christian Education'),
    ('CED', 'Christian Education'),
    ('CEI', 'Christian Education'),
    ('CH', 'Church History'),
    ('CHED', 'Christian Education'),
    ('CHEM', 'Chemistry'),
    ('CHIN', 'Chinese'),
    ('CHM', 'Church Ministries'),
    ('CHP', 'Chaplaincy'),
    ('CLC', 'Counseling'),
    ('CLD', 'Church Leadership'),
    ('CLG', 'Counseling'),
    ('CMCC', 'Contemporary Music Centre CCCU'),
    ('CMPT', 'Computer Sciences'),
    ('COMM', 'Communications'),
    ('COOP', 'Cooperative Education'),
    ('CPL', 'Church Planting'),
    ('CPNC', 'Counselling  Psyc Non Credit'),
    ('CPR', 'CPR and First Aid Certificatio'),
    ('CPSY', 'Counseling Psychology'),
    ('DMN', 'Doctor of Ministry'),
    ('DRAM', 'Drama'),
    ('DS', 'Unapproved Directed Study'),
    ('ECON', 'Economics'),
    ('EDUC', 'Education'),
    ('ELCE', 'Office of the Dean'),
    ('ENGL', 'English'),
    ('ENVS', 'Environmental Studies'),
    ('ESLI', 'English as a Second Language'),
    ('ESNC', 'ESLI Non Credit'),
    ('FINE', 'Fine Arts'),
    ('FREN', 'French'),
    ('FSC', 'Family & Soc Science (Korean)'),
    ('FSUR', 'Geography'),
    ('GEOG', 'Geography'),
    ('GEOL', 'Geology'),
    ('GERM', 'German'),
    ('GLNC', 'Global Learning Connections'),
    ('GREE', 'Greek'),
    ('HEBR', 'Hebrew'),
    ('HIC', 'Church History'),
    ('HIS', 'Church History'),
    ('HIST', 'History'),
    ('HKIN', 'Human Kinetics'),
    ('HSER', 'Human Services'),
    ('HUMA', 'Humanities'),
    ('HUMN', 'Humanities and Social Services'),
    ('IDIS', 'Interdisciplinary Studies'),
    ('INT', 'Internship'),
    ('ISC', 'Indepent Studies'),
    ('ISYS', 'Information Systems'),
    ('JAPA', 'Japanese'),
    ('LAST', 'Latin American Studies (CCCU)'),
    ('LATI', 'Religious Studies'),
    ('LATN', 'Latin'),
    ('LBR', 'Library'),
    ('LDC', 'Leadership Studies'),
    ('LDR', 'Leadership Studies'),
    ('LDRS', 'Leadership'),
    ('LIN', 'Linguistics'),
    ('LING', 'Linguistics'),
    ('LLC', 'Laurentian Leadership Centre'),
    ('MATH', 'Mathematics'),
    ('MCS', 'MA in Christian Studies'),
    ('MEST', 'Middle East Studies (CCCU)'),
    ('MIC', 'Missions'),
    ('MIS', 'Missions'),
    ('MLE', 'Master of Linguistics Exeges'),
    ('MM1', 'Master of Ministry One'),
    ('MM2', 'Master of Ministry Two'),
    ('MM3', 'Master of Ministry Three'),
    ('MMI', 'Master of Ministry'),
    ('MNF', 'Ministry Formation'),
    ('MRE', 'Master of Religious Education'),
    ('MRP', 'Ministry Research Project'),
    ('MTH', 'Master of Theology'),
    ('MTS', 'Master of Theological Studies'),
    ('MTSC', 'Master of Theo in Counseling'),
    ('MUSI', 'Music'),
    ('NATS', 'Natural Science'),
    ('NURS', 'Nursing'),
    ('OMC', 'Outreach Ministries'),
    ('OMI', 'Outreach Ministries'),
    ('OMT', 'Outreach Ministries'),
    ('PDEV', 'Prof. Dev./Non Credit'),
    ('PDTC', 'Professional Development (GLC)'),
    ('PHED', 'Physical Education'),
    ('PHIL', 'Philosophy'),
    ('PHYS', 'Physics'),
    ('POLS', 'Political Science'),
    ('PREP', 'Career Preparation'),
    ('PSYC', 'Psychology'),
    ('PTC', 'Pastoral Theology'),
    ('PTH', 'Pastoral Theology'),
    ('RCE', 'Religion Culture and Ethics'),
    ('RCE5', 'Religion Culture and Ethics'),
    ('RECR', 'Recreation'),
    ('RELS', 'Religious Studies'),
    ('RES', 'Research Studies'),
    ('RIST', 'Roehampton Inst Studies (CCCU)'),
    ('RSHP', 'Relationships Non Credit'),
    ('RUSS', 'Russian'),
    ('RUST', 'Russian Studies (CCCU)'),
    ('SCS', 'Science Studies (Korean)'),
    ('SIJO', 'Sum Inst of Journalism (CCCU)'),
    ('SKLS', 'Study Skills'),
    ('SOCI', 'Sociology'),
    ('SOCS', 'Humanities and Soc Services'),
    ('SPAN', 'Spanish'),
    ('STUD', 'Enrolment Services'),
    ('TENC', 'TESL Non Credit'),
    ('TEST', 'Test - Enrolment Services Only'),
    ('THC', 'Theological Studies'),
    ('THS', 'Theological Studies'),
    ('TNET', 'Training Network'),
    ('TRAN', 'Transfer Credit - Unspecified'),
    ('TRVL', 'Enrolment Services'),
    ('UNIV', 'Student Life'),
    ('WLS', 'Worship Leadership Studies'),
    ('WMS', 'Womens Ministry Studies'),
    ('WSNC', 'Worship Studies Non Credit'),
    ('WSTU', 'Worship Studies'),
    ('WVS', 'Worldview Studies (Korean)'),
    ('ZOOL', 'Biology'),
)
class Course(models.Model):
    """
    Basic course data
    """
    department = models.CharField(max_length=4, choices=DEPARTMENT_CHOICES)
    number = models.CharField(max_length=3)

    class Meta:
        ordering = ('department', 'number')

    def code(self):
        return "%s %s" % (self.department, self.number)

    def __unicode__(self):
        return self.code()

class MetaBook(models.Model):
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
    def title_list(self):
        return self.author

class Book(models.Model):
    """
    For when a student lists a particular copy of a book.
    Keeps track of 
        * when and who listed (is selling) it
        * if and who is currently holding it
        * when it was last put on hold
	* when it finally got sold
	* whether the book is flagged for deletion or not
    """
    STATUS_CHOICES = (
        (u'F', u'For Sale'),
        (u'M', u'Missing'),
        (u'O', u'On Hold'),
        (u'P', u'Seller Paid'),
        (u'S', u'Sold'),
        (u'T', u'To Be Deleted'),
        (u'D', u'Deleted'),
    )

    metabook = models.ForeignKey(MetaBook)
    list_date = models.DateTimeField('Date Listed', auto_now_add=True)
    seller = models.ForeignKey(User, related_name="selling")
    sell_date = models.DateTimeField('Date Sold', blank=True, null=True)
    holder = models.ForeignKey(User, related_name="holding",
                               blank=True, null=True)
    hold_date = models.DateTimeField('Date Held', blank=True, null=True)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='F')
    is_legacy = models.BooleanField(default=False)

    def __unicode__(self):
        return "%s by %s on %s" % (self.metabook, self.seller,
	                           self.list_date.date())
class Log(models.Model):
    """
    Keeps track of all actions taken on Books
    """
    ACTION_CHOICES = (
        (u'A', u'Added Book'), # -> For Sale
        (u'M', u'Marked as Missing'), # -> Missing
        (u'O', u'Placed on Hold'), # -> On Hold
        (u'X', u'Extended Hold'), # -> On Hold
        (u'R', u'Removed Hold'), # -> For Sale
        (u'P', u'Paid Seller'), # -> Seller Paid
        (u'S', u'Sold'), # -> Sold
        (u'T', u'Marked as To Be Deleted'), # -> To Be Deleted
        (u'D', u'Deleted'), # -> Deleted
        (u'E', u'Edited'), # -> Same Status
    )
    action = models.CharField(max_length=1, choices=ACTION_CHOICES)
    when = models.DateTimeField(auto_now_add=True)
    book = models.ForeignKey(Book, related_name="logs")
    who = models.ForeignKey(User, related_name="actions")

    def __unicode__(self):
        return "%s %s" % (self.who.get_full_name(), self.when)
