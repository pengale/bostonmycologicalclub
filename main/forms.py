from models import *
from django.contrib.auth.models import User
from django.forms import (ModelForm, Form, TextInput, DateField, 
                          TimeField, BooleanField, CharField,
                          Textarea, IntegerField, EmailField)
from kungfutime import KungfuTimeField

# Walk Editing Forms

class WalkForm(ModelForm):
    time = KungfuTimeField()
    permission = BooleanField(
        required=True,
        help_text = """
Has permission to use the area been granted? (required)""",
        )

    class Meta:
        model = Walk
        exclude = ('creator', 'mushrooms_found', 'public')

class WalkFormAdmin(WalkForm):
    time = KungfuTimeField()
    permission = BooleanField(
        required=True,
        help_text = """
Has permission to use the area been granted? (required)""",
        )

    class Meta:
        model = Walk
        exclude = ('creator', 'mushrooms_found')

class WalkMushroomForm(ModelForm):
    class Meta:
        model = Walk
        fields = ('terrain', 'weather', 'mushrooms_found')

# Membership and User Forms

class MembershipForm(ModelForm):
    class Meta:
        model = Membership

class MembershipFetch(Form):
    membership_id = IntegerField()

class MembershipSearch(Form):
    last_name = CharField(max_length=30)
        
class UserForm(ModelForm):
    """ Form to create a new user via the mushroom_admin.  

    """

    class Meta:
        model = User
        exclude = (
            'user_permissions', 
            'password',
            'is_superuser',
            'last_login',
            'groups',
            'is_staff',
            )

class NewUserForm(UserForm):
#@@@ Not sure if this is actually used for anything at present
    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError("""
A user with that username already exists.""")


class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user', 'membership')

class DueForm(ModelForm):
    notes = CharField(widget=Textarea(
            attrs={'rows':'2'}), required=False)
    class Meta:
        model = Due
        exclude = ('membership')

class MembershipStatus(ModelForm):
    class Meta:
        model = User
        fields = ('is_active')

class NewsbitForm(ModelForm):
    class Meta:
        model = Newsbit

class PageForm(ModelForm):
    class Meta:
        model = Page

class AnnouncementForm(ModelForm):
    class Meta:
        model = Announcement

# Forms for allowing a User to edit their info

class UserEditsUser(ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class UserEditsProfile(ModelForm):
    class Meta:
        model = UserProfile
        fields = ('areas', 'want_email', 'phone', 'alt_phone')
    
class UserEditsMembership(ModelForm):
    class Meta:
        model = Membership
        fields = ('address', 'address2', 'city', 'state',
            'zip', 'country')

# Email Forms

class EmailForm(Form):
    subject = CharField(max_length=200)
    message = CharField(widget=(Textarea))
    
