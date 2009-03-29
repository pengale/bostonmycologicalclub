from models import Walk, Membership, UserProfile, Due
from django.contrib.auth.models import User
from django.forms import (ModelForm, Form, TextInput, DateField, 
                          TimeField, BooleanField, CharField,
                          Textarea, IntegerField)
from kungfutime import KungfuTimeField

# Walk Editing Forms

class WalkForm(ModelForm):
#    date = DateField(widget=TextInput(
#            attrs={'class':'vDateField'}))
#    time = KungfuTimeField(widget=TextInput(
#            attrs={'class':'vTimeField'}))
    time = KungfuTimeField()

    class Meta:
        model = Walk
        exclude = ('creator', 'mushrooms_found')

class WalkMushroomForm(ModelForm):
    class Meta:
        model = Walk
        fields = ('mushrooms_found')

# Membership and User Forms

class MembershipForm(ModelForm):
    class Meta:
        model = Membership

class MembershipSearch(Form):
    membership_id = IntegerField()

class UserForm(ModelForm):
    class Meta:
        model = User
        exclude = (
            'user_permissions', 
            'password',
            'email',
            'is_superuser',
            'last_login',
            'groups',
            'is_staff',
            )

class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user', 'membership')

class DueForm(ModelForm):
    notes = CharField(widget=Textarea(
            attrs={'rows':'2'}))
    class Meta:
        model = Due
        exclude = ('membership')

class MembershipStatus(ModelForm):
    class Meta:
        model = User
        fields = ('is_active')

# Forms for allowing a User to edit their info

class UserEditsUser(ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username')

class UserEditsProfile(ModelForm):
    class Meta:
        model = UserProfile
        fields = ('areas', 'want_email')
    
class UserEditsMembership(ModelForm):
    class Meta:
        model = Membership
        fields = ('address', 'address2', 'city', 'state',
            'zip', 'country')
