from django.db import models
from bmc.settings import *
from django.contrib.auth.models import User
from django.contrib.localflavor.us.models import USStateField, PhoneNumberField
from django import forms
import datetime

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
    organization = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=50)
    address2 = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=60)
    state = USStateField()
    zip = models.CharField(max_length=10)
    country = models.CharField(
        max_length=50, 
        default="United States of America",
        blank=True,
        )

    # Remarks
    notes = models.TextField(blank=True)

    # Type
    membership_type = models.CharField(
        max_length=20, 
        choices=MEMBERSHIP_TYPES
        )

    def get_profiles(self):
        model = models.get_model('main', 'UserProfile')
        profiles = model.objects.filter(membership=self)
        return profiles

    def get_most_recent_due(self):
        model = models.get_model('main', 'Due')
        dues = model.objects.filter(membership=self)
        try:
            due = dues[0]
        except IndexError:
            return '--'
        return due

    def get_name_list(self):
        profiles = self.get_profiles()
        try:
            name_list = ' & '.join(
                (profile.user.last_name + ', ' + profile.user.first_name
                 ) for profile in profiles)
        except:    #@@@ Evil generic exception
            name_list = 'blank'            

        return name_list

    def get_anded_name_list(self):
        """ Get name list in a friendly format for the report 

        @@@Should be intelligently combined with get_name_list
        """

        profiles = self.get_profiles()
        try:
            name_list = ' and '.join(
                ('%s %s' % (profile.user.first_name, profile.user.last_name)
                 ) for profile in profiles)
        except:    #@@@ Evil generic exception
            name_list = 'blank'            

        return name_list
        

    def get_email_list(self):
        profiles = self.get_profiles()
        try:
            email_list = ', '.join(
                (profile.get_email()
                 ) for profile in profiles)
        except:    #@@@ Evil generic exception
            email_list = 'blank'            

        return email_list


    def is_active(self):
        profiles = self.get_profiles()
        for profile in profiles:
            try:
                if profile.user.is_active:
                    return True
            except:
                pass
            
        return False

    def __unicode__(self):
        return  '%s: %s, %s, %s' % (
            self.get_name_list(),
            self.address, 
            self.city, self.state,
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

    def __unicode__(self):
        return  '%s' % (self.payment_amount)


class UserProfile(models.Model):
    """ Expands the User class in contrib.auth.models to include some
    BMC specific stuff.
    """
    # Membership
    membership = models.ForeignKey(Membership)

    # Name, Title
    title = models.CharField(max_length=200, blank=True)
    
    # Contact Info
    phone = PhoneNumberField(blank=True)
    alt_phone = PhoneNumberField(blank=True)

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
    want_email = models.BooleanField(default=True)
    areas = models.ManyToManyField(WalkArea)
    user = models.ForeignKey(User, unique=True, blank=True)

    # Notes
    notes = models.TextField(blank=True)

    def get_email(self):
        """ Return email address.

        Return None if the email address is the filler email from the
        import.
        """ 
        email = self.user.email
        if email == "NoEmail@BostonMycologicalClub.Org": 
            return None
        return email

    def __unicode__(self):
        try:
            first_name = self.user.first_name
            last_name = self.user.last_name
        except User.DoesNotExist:
            first_name = "blank"
            last_name = "profile"
        return  '%s %s' % (first_name, last_name)


class Walk(models.Model):
    """ One of the most import thing that members can do is create
    walks.
    """
    # Who, Why, When
    creator = models.ForeignKey(User)

    from django.forms import TextInput
    date = models.DateField()
    time = models.TimeField()
    public = models.BooleanField(default=False)

    # Where
    location = models.TextField()
    meeting_place = models.TextField()
    latitude = models.DecimalField(
        max_digits=9, decimal_places=7, 
        blank=True, 
        null=True,
        help_text = 'You may leave this blank.',
        )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=7, 
        blank=True, 
        null=True,
        help_text = 'You may leave this blank.',
        )
    permission = models.BooleanField(
        help_text = 'Has permission to use the area been granted?',
        )
    directions = models.TextField(verbose_name="Address and Directions")
    weather = models.TextField(blank=True) 
    terrain = models.TextField(blank=True)
    areas = models.ManyToManyField(WalkArea)

    # Notes
    mushrooms_found = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    def __unicode__(self):
        return '%s %s' % (self.location, self.date)

    class Meta:
        ordering = ["-date"]

class Announcement(models.Model):
    """ Announcements for the front page.  
    """
    timestamp = models.DateTimeField(default=datetime.datetime.now())
    heading = models.CharField(max_length=40)
    summary = models.TextField()
    full_story = models.TextField(blank=True)
    picture = models.FileField(upload_to='uploaded_pics/', blank=True,);
    picture_caption = models.TextField(blank=True)

    class Meta:
        ordering = ["-timestamp"]

    def __unicode__(self):
        return  '%s' % (self.heading)

class Newsbit(models.Model):
    """ Quick news blurbs to go on the front page for stuff that
    doesn't need a full announcement.
    """
    timestamp = models.DateTimeField(
        default=datetime.datetime.now()
        )
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

class Nugget(models.Model):
    """ A brief fact about the BMC
    """
    active = models.BooleanField(
        default=True,
        help_text="uncheck this box if you do not want the fact to show up on the site"
        )
    text = models.TextField()

    def __unicode__(self):
        if self.active:
            status = "active"
        else:
            status = "disabled"
        return '%s (%s)' % (self.text, status)


class Page(models.Model):
    """ A generic page.  
    """
    name = models.CharField(max_length=30)
    text = models.TextField()

    def __unicode__(self):
        return '%s' % (self.name)


