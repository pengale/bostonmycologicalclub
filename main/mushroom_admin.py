""" Script telling the mushroom admin where to find Models and Model
Forms for the stuff in it. """

from models import *
from forms import *

class entries():
    """ Methods and info attached to a class of entries in the
    mushroom admin (a walk, membership, newsbit, etc.)"""
    MODEL = ''
    FORM = ''
    NAME = ''
    VIEW_TEMPLATE = 'view_entry.html'  # rarely gets used
    EDIT_TEMPLATE = 'edit_entry.html'
    LIST_TEMPLATE = 'list_entries.html'

    def save_entries(self, form):
        """ Attempt to save a form. """
        try:
            form.save()
            return True
        except:
            return False

    def edit_permission(self):
        """ """
        return False
    

class newsbits(entries):
    MODEL = Newsbit
    FORM = NewsbitForm
    NAME = 'newsbit'

class announcements(entries):
    MODEL = Announcement
    FORM = AnnouncementForm
    NAME = 'announcement'

class pages(entries):
    MODEL = Page
    FORM = PageForm
    NAME = 'page'



