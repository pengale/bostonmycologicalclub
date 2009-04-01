from django.db import models
from bmc.settings import *
from django.contrib.auth.models import User
from django.contrib.localflavor.us.models import USStateField
from django import forms

class WalkArea(models.Model):
    """ Members might only want to hear about walks in their area.
    """
    name = models.CharField(max_length=40)

    def __unicode__(self):
        return self.name

class Membership(models.Model):
    """ Each BMC Membership is tied to a specific address; multiple
    members of the same household can have different usernames.
    """
    # Dates
    join_date = models.DateField()

    # Address
    address = models.CharField(max_length=50)
    address2 = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=60)
    state = USStateField()
    zip = models.CharField(max_length=10)
    country = models.CharField(
        max_length=50, 
        default="United States of America"
        )

    # Remarks
    notes = models.TextField(blank=True)

    # Type
    membership_type = models.CharField(
        max_length=20, 
        choices=MEMBERSHIP_TYPES
        )

    def __unicode__(self):
        return  '%s, %s, %s' % (
            self.address, 
            self.city, self.state
            )

    class Meta:
        ordering = ["-join_date"]


class Due(models.Model):
    """ Tracks whether and when dues are due, when they've been paid,
    etc.    
    """
    membership = models.ForeignKey(Membership)
    payment_date = models.DateField()
    payment_amount = models.DecimalField(
        max_digits=6, 
        decimal_places=2,
        )
    payment_type = models.CharField(max_length=20)
    paid_thru = models.DateField() # best way to do this?
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-paid_thru"]



class UserProfile(models.Model):
    """ Extends the User class in contrib.auth.models to include some
    BMC specific stuff.
    """
    # Membership
    membership = models.ForeignKey(Membership)

    # Name, Title
    title = models.CharField(max_length=200, blank=True)
    
    # Contact Info
    #phone = models.PhoneNumberField()
    #phone2 = models.PhoneNumberField()

    # Type
    # we need a few special user types in addition to staff and superusers
    #is_walk_moderator = models.BooleanField(
    #    _('walk moderator status'), 
    #    default=False, 
    #    help_text=_("Walk Moderators can create and modify walks.")
    #    )

    #is_ID_committee = models.BooleanField(
    #    _('ID Committee Member status'), 
    #    default=False, 
    #    help_text=_("ID Committee members can create and edit ID Sessions.")
    #    )

    # Preferences
    want_email = models.BooleanField()
    areas = models.ManyToManyField(WalkArea)
    user = models.ForeignKey(User, unique=True, blank=True)

    def __unicode__(self):
        return  '%s' % (self.user)


class Walk(models.Model):
    """ One of the most import thing that members can do is create
    walks.
    """
    # Who, Why, When
    creator = models.ForeignKey(User)

    from django.forms import TextInput
    date = models.DateField()
    time = models.TimeField()

    # Where
    meeting_place = models.CharField(max_length=300)
    collecting_area = models.CharField(max_length=300)
    lat = models.DecimalField(
        max_digits=7, decimal_places=4, blank=True,
        help_text = 'You may leave this blank.',
        )
    long = models.DecimalField(
        max_digits=7, decimal_places=4, blank=True,
        help_text = 'You may leave this blank.',
        )
    permission = models.BooleanField(
        help_text = 'Has permission to use the area been granted?'
        )
    directions = models.TextField()
    weather = models.TextField() 
    terrain = models.TextField()
    areas = models.ManyToManyField(WalkArea)

    # Notes
    mushrooms_found = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return '%s %s' % (self.location, self.date)

    class Meta:
        ordering = ["-date"]

class Announcement(models.Model):
    """ Announcements for the front page.  
    """
    timestamp = models.DateTimeField()
    heading = models.CharField(max_length=40)
    summary = models.TextField()
    full_story = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-timestamp"]

    def __unicode__(self):
        return  '%s' % (self.heading)

class Newsbit(models.Model):
    """ Quick news blurbs to go on the front page for stuff that
    doesn't need a full announcement.
    """
    timestamp = models.DateTimeField()
    news = models.TextField()

    class Meta:
        ordering = ["-timestamp"]

    def __unicode__(self):
        return  '%s' % (self.news)

class PublicWalk(models.Model):
    """ Publicly posted walks (not all walks are public).  
    """
    when = models.DateTimeField()
    collecting_area = models.CharField(max_length=100)
    meeting_place = models.TextField()

    class Meta:
        ordering = ["when"]

    def __unicode__(self):
        return '%s' % (self.collecting_area)

class IDSession(models.Model):
    """ Session for IDing mushrooms. 
    """
    when = models.DateTimeField()
    where = models.CharField(max_length=50, default='Farlow Herbarium')

    class Meta:
        ordering = ["when"]

    def __unicode__(self):
        return '%s' % (self.when)

class Page(models.Model):
    """ A generic page.  
    """
    name = models.CharField(max_length=30)
    text = models.TextField()

    
