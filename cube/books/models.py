# Copyright (C) 2010  Trinity Western University

from datetime import datetime
from django.db import models
from django.contrib.auth.models import User

DEPARTMENT_CHOICES = (
    ('ALDR', 'ALDR - MA Leadership'),
    ('ANTH', 'ANTH - Anthropology'),
    ('ART ', 'ART  - Art'),
    ('ASWN', 'ASWN - Austria Exchange Program'),
    ('AVIA', 'AVIA - Aviation'),
    ('BIE ', 'BIE  - Bible Exposition'),
    ('BIL ', 'BIL  - Biblical Languages'),
    ('BIOL', 'BIOL - Biology'),
    ('BIOT', 'BIOT - Biotechnology'),
    ('BUSI', 'BUSI - Business'),
    ('CAP ', 'CAP  - Contemporary Apologetics'),
    ('CATH', 'CATH - Catholicism'),
    ('CCM ', 'CCM  - Cross Cultural Ministries'),
    ('CED ', 'CED  - Christian Education'),
    ('CHEM', 'CHEM - Chemistry'),
    ('CHIN', 'CHIN - Chinese'),
    ('CHM ', 'CHM  - Church Ministries'),
    ('CHP ', 'CHP  - Chaplaincy'),
    ('CLD ', 'CLD  - Christian Leadership Develop.'),
    ('CLG ', 'CLG  - Counseling'),
    ('CMPT', 'CMPT - Computer Sciences'),
    ('COMM', 'COMM - Communications'),
    ('COOP', 'COOP - Cooperative Education'),
    ('CPL ', 'CPL  - Church Planting'),
    ('CPSY', 'CPSY - Counselling Psychology'),
    ('DMN ', 'DMN  - Doctor of Ministry'),
    ('DRAM', 'DRAM - Drama'),
    ('DS  ', 'DS   - Unapproved Directed Study'),
    ('ECON', 'ECON - Economics'),
    ('EDUC', 'EDUC - Education'),
    ('ELCE', 'ELCE - English Language Competency'),
    ('ENGL', 'ENGL - English'),
    ('ENVS', 'ENVS - Environmental Studies'),
    ('ESLI', 'ESLI - English as a Second Language'),
    ('ESLP', 'ESLP - ESLI Pre-Masters'),
    ('ESNC', 'ESNC - ESLI Non Credit'),
    ('FINE', 'FINE - Fine Arts'),
    ('FREN', 'FREN - French'),
    ('FSC ', 'FSC  - Family & Soc Science (Korean)'),
    ('GEOG', 'GEOG - Geography'),
    ('GEOL', 'GEOL - Geology'),
    ('GERM', 'GERM - German'),
    ('GLNC', 'GLNC - Global Learning Connections'),
    ('GREE', 'GREE - Greek'),
    ('HEBR', 'HEBR - Hebrew'),
    ('HIS ', 'HIS  - Church History'),
    ('HIST', 'HIST - History'),
    ('HKIN', 'HKIN - Human Kinetics'),
    ('IDIS', 'IDIS - Interdisciplinary Studies'),
    ('INT ', 'INT  - Internship'),
    ('ISYS', 'ISYS - Information Systems'),
    ('JAPA', 'JAPA - Japanese'),
    ('LAST', 'LAST - Latin American Studies (CCCU)'),
    ('LATN', 'LATN - Latin'),
    ('LBR ', 'LBR  - Library'),
    ('LDR ', 'LDR  - Leadership Studies'),
    ('LDRS', 'LDRS - Leadership'),
    ('LIN ', 'LIN  - Linguistics'),
    ('LING', 'LING - Linguistics'),
    ('LLC ', 'LLC  - Laurentian Leadership Centre'),
    ('MATH', 'MATH - Mathematics'),
    ('MBA ', 'MBA  - Master of Business Admin'),
    ('MCS ', 'MCS  - MA in Christian Studies'),
    ('MIS ', 'MIS  - Missions'),
    ('MLE ', 'MLE  - Master of Linguistics Exeges'),
    ('MNF ', 'MNF  - Ministry Formation'),
    ('MTH ', 'MTH  - Master of Theology'),
    ('MTS ', 'MTS  - Master of Theological Studies'),
    ('MUSA', 'MUSA - Music (Private Lessons)'),
    ('MUSI', 'MUSI - Music'),
    ('NATS', 'NATS - Natural Science'),
    ('NURS', 'NURS - Nursing'),
    ('PHIL', 'PHIL - Philosophy'),
    ('PHYS', 'PHYS - Physics'),
    ('POLS', 'POLS - Political Science'),
    ('PREP', 'PREP - Career Preparation'),
    ('PSYC', 'PSYC - Psychology'),
    ('PTH ', 'PTH  - Pastoral Theology'),
    ('RCE ', 'RCE  - Religion Culture and Ethics'),
    ('RECR', 'RECR - Recreation'),
    ('RELS', 'RELS - Religious Studies'),
    ('RES ', 'RES  - Research Studies'),
    ('RUSS', 'RUSS - Russian'),
    ('SCS ', 'SCS  - Science Studies (Korean)'),
    ('SKLS', 'SKLS - Study Skills'),
    ('SOCI', 'SOCI - Sociology'),
    ('SOCS', 'SOCS - Humanities and Soc Services'),
    ('SPAN', 'SPAN - Spanish'),
    ('STUD', 'STUD - Enrolment Services'),
    ('THS ', 'THS  - Theological Studies'),
    ('THTR', 'THTR - Theatre'),
    ('TRVL', 'TRVL - Enrolment Services'),
    ('TUTX', 'TUTX - Twu/TUT Exchange Program'),
    ('UNIV', 'UNIV - University 101'),
    ('WLS ', 'WLS  - Worship Leadership Studies'),
    ('WRTG', 'WRTG - Writing'),
    ('WSTU', 'WSTU - Worship Studies'),
    ('WVS ', 'WVS  - Worldview Studies (Korean)'),
)

class Course(models.Model):
    """
    Basic course data
    """
    department = models.CharField(max_length=4, choices=DEPARTMENT_CHOICES)
    number = models.CharField(max_length=3)

    class Meta:
        ordering = ('department', 'number')
        unique_together = ("department", "number")

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
    barcode = models.CharField(max_length=50, unique=True)
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
        (u'D', u'Deleted'),
        (u'T', u'To Be Deleted'),
    )

    metabook = models.ForeignKey(MetaBook)
    list_date = models.DateTimeField('Date Listed', default=datetime.now)
    seller = models.ForeignKey(User, related_name="selling")
    sell_date = models.DateTimeField('Date Sold', blank=True, null=True)
    holder = models.ForeignKey(User, related_name="holding", blank=True, null=True)
    hold_date = models.DateTimeField('Date Held', blank=True, null=True)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='F')
    is_legacy = models.BooleanField(default=False)

    def __unicode__(self):
        return "%s listed by %s on %s" % (self.metabook, self.seller, self.list_date.date())
   
    # Looks in the logs to find the last status that this book had
    def previous_status(self):
		action_to_choice = {
			'A' : 'F', # -> For Sale
			'M' : 'M', # -> Missing
			'O' : 'O', # -> On Hold
			'X' : 'O', # -> On Hold
			'R' : 'F', # -> For Sale
			'P' : 'P', # -> Seller Paid
			'S' : 'S', # -> Sold
			'T' : 'T', # -> To Be Deleted
			'D' : 'D', # -> Deleted
		}

		# There are some log actions that don't correspond to a book status, if the previous
		# action is one of these, discard it and go to the action before that, etc...
		history = Log.objects.all()
		#history = Log.objects.filter(book=self.id).exclude(action_in['D', 'E', 'U']).order_by('when')
		#history = Log.objects.filter(book=self.id).exclude(action='D').exclude(action='E').exclude(action='U').order_by('when').reverse()
        
        # Loop through previous logs and return it if it is in our STATUS_CHOICES
		for log_point in history:
			if log_point.action in action_to_choice.keys():
				return action_to_choice[log_point.action]
		return ''

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
        (u'U', u'Undeleted'), # -> Previous non-deleted status 
    )
    action = models.CharField(max_length=1, choices=ACTION_CHOICES)
    when = models.DateTimeField(default=datetime.now)
    book = models.ForeignKey(Book, related_name="logs")
    who = models.ForeignKey(User, related_name="actions")

    def __unicode__(self):
        return "%s %s" % (self.who.get_full_name(), self.when)
