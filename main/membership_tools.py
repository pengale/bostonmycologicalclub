""" Tools for adding, editing and changing Memberships, along w/
associated user and user profiles.  """

from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from forms import (MembershipForm, UserForm, UserProfileForm, 
                   DueForm, MembershipStatus, MembershipSearch)
from models import Membership, UserProfile, User, Due
from django.contrib.auth.models import User, UserManager
from views import error_404

def list_users(member):
    """ Returns a list of users associated with a membership """
    users = []
    user_profiles = UserProfile.objects.filter(membership=member.id)
    
    for profile in user_profiles:
        user = User.objects.get(id=profile.user.id)
        users.append(user)

    return users

def list_memberships(request, criteria=None):
    """ List all members. """
    if criteria == 'late':
        members = Membership.objects.all()
        
    else:
        members = Membership.objects.all()
    
    member_list = []
    for m in members:
        users = list_users(m)
        mem_blob = { 'membership' : m, 'users' : users }
        member_list.append(mem_blob)

    template = 'memberlist.html'
    ctxt = { 'member_list' : member_list, 'request' : request }
    return render_to_response(template, ctxt)

def edit_membership(request, membership=None):
    """ Edit an existing membership, or add a new membership if none
    specified. """

    # Fetch membership object
    if membership: 
        membership = int(membership)
        try: 
            membership = Membership.objects.get(id=membership)

        except ObjectDoesNotExist:
            error = "That Membership does not appear to exist."
            return error_404(request, error)

        
    # Attempt to save the Membership
    if request.method == 'POST':
        if membership:
            # save an existing membership
            form = MembershipForm(request.POST, instance=membership)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(
                    '/members/' + str(membership.id) + '/view/'
                    )

            else:
                form = MembershipForm(request.POST)
                template = 'edit_membership.html'
                ctxt = { 
                    'form' : form, 
                    'request' : request, 
                    'membership' : membership 
                    }
                return render_to_response(template, ctxt)

        else:
            # save a new membership
            form = MembershipForm(request.POST)
            if form.is_valid():
                membership = form.save()
                return HttpResponseRedirect(
                    '/members/' + str(membership.id) + '/view/'
                    )

            else:
                form = MembershipForm(request.POST)
                template = 'edit_membership.html'
                ctxt = { 
                    'form' : form, 
                    'request' : request, 
                    'membership' : membership 
                    }

            return render_to_response(template, ctxt)
    
    # Return a page to edit the membership
    elif membership:
        form = MembershipForm(instance=membership)
        template = 'edit_membership.html'
        ctxt = { 
            'form' : form, 
            'request' : request, 
            'membership' : membership,
            }
        return render_to_response(template, ctxt)


    # Return a blank membership form
    else: 
        form = MembershipForm()
        template = 'edit_membership.html'
        ctxt = { 
            'form' : form, 
            'request' : request, 
            'membership' : membership,
            }
        return render_to_response(template, ctxt)

def create_membership(request):
    edit_member(request, membership=None)


def edit_user(request, membership, user=None):
    """ Edit an existing user, or add a new one if no user specified
    """

    # Make sure that we are attempting to attach to a valid
    # membership.
    try:
        membership = Membership.objects.get(id=membership)

    except ObjectDoesNotExist:
        error = "That Membership does not appear to exist."
        return error_404(request, error)

    # And make sure that we're talking about a valid user, if user was
    # specified.
    if user:
        user = int(user)
        try:
            user = User.objects.get(id=user)
            profile = UserProfile.objects.get(user=user)
            
        except ObjectDoesNotExist:
            error = """That user does not exist, or you are attempting
            to edit a user without a profile (you must use the admin
            interface to edit this sort of user)."""
            return error_404(request, error)

    if request.method == 'POST':
        if user:
            # save changes to an existing user
            user_form = UserForm(request.POST, instance=user)
            profile_form = UserProfileForm(request.POST, instance=profile)
            if user_form.is_valid() and profile_form.is_valid():
                user = user_form.save(commit=False)
                user.email = user.username
                user.save()
                user_form.save_m2m()
                profile = profile_form.save()

                return HttpResponseRedirect(
                    '/members/' + str(membership.id) + '/view/'
                    )
            else:
                template = 'edit_user.html'
                ctxt = { 
                    'request' : request, 
                    'membership' : membership,
                    'user' : user.id,
                    'edit_user' : user_form,
                    'edit_profile' : profile_form,
                    }
                return render_to_response(template, ctxt)


        else:
            # save a new user
            user_form = UserForm(request.POST)
            profile_form = UserProfileForm(request.POST)
            if user_form.is_valid() and profile_form.is_valid():
                user = user_form.save(commit=False)
                user.email = user.username
                user.save()
                user_form.save_m2m()
                profile = profile_form.save(commit=False)
                profile.user = User.objects.get(id=user.id)
                profile.membership = membership
                profile.save()
                profile_form.save_m2m()
                return HttpResponseRedirect(
                    '/members/' + str(membership.id) + '/view/'
                    )

            else:
                template = 'edit_user.html'
                ctxt = { 
                    'request' : request, 
                    'membership' : membership,
                    'user' : None,
                    'edit_user' : user_form,
                    'edit_profile' : profile_form,
                    }
                return render_to_response(template, ctxt)

    elif user:
        template = 'edit_user.html'
        ctxt = { 
            'request' : request, 
            'membership' : membership,
            'user' : user.id,
            'edit_user' : UserForm(instance=user),
            'edit_profile' : UserProfileForm(instance=profile),
            }
        return render_to_response(template, ctxt)

    else:
        # return a  blank user form
        template = 'edit_user.html'
        ctxt = { 
            'request' : request, 
            'membership' : membership,
            'user' : None,
            'edit_user' : UserForm(),
            'edit_profile' : UserProfileForm(),
            }
        return render_to_response(template, ctxt)

        
def membership_status(request, membership, suspend_restore):
    membership = int(membership)
    # Fetch membership
    try: 
        membership = Membership.objects.get(id=membership)
        
    except ObjectDoesNotExist:
        error = "That Membership does not appear to exist."
        return error_404(request, error)

    # Fetch users
    try:
        profiles = UserProfile.objects.filter(membership=membership)
    except ObjectDoesNotExist:
        error = """ This Membership does not seem to have any users
        attached to it."""
        return error_404(request, error)
        

    if request.method == 'POST':
        for profile in profiles:
            user = profile.user
            form = MembershipStatus(request.POST, instance=user)
            if form.is_valid():
                form.save()
            else:
                error = """ The form you submitted isn't valid.
                    Either you're trying to do hacky things to the
                    site (solution: please stop), or there's an error
                    in the code (solution: please get in touch with
                    you system admin)."""
                return error_404(request, error)

        return HttpResponseRedirect(
            '/members/' + str(membership.id) + '/view/'
            )

    else:
        status = True
        if suspend_restore == 'suspend': status = False

        template = "membership_status.html"
        ctxt = { 
            'request' : request, 
            'status' : status,
            'form' : MembershipStatus(),
            }
        return render_to_response(template, ctxt)


def view_membership(request, membership):
    """ View Details of a Membership """

    try:
        membership = Membership.objects.get(id=membership)
        dues = Due.objects.filter(membership=membership)
        user_profiles = UserProfile.objects.filter(membership=membership)

        edit_user = UserForm()
        edit_profile = UserProfileForm()
        edit_due = DueForm()

        # is the membership active?  
        active = False  # we assume not ...
        for profile in user_profiles:
            # ... but only one user needs to be active in order for
            # the whole membership to be 'active' (this allows us to
            # turn off one username without wiping the whole profile)
            if profile.user.is_active:
                active = True            

        
        template = 'view_membership.html'
        ctxt = {
            'request' : request,
            'membership' : membership,
            'dues' : dues,
            'user_profiles' : user_profiles,
            'edit_user' : edit_user,
            'edit_profile' : edit_profile,
            'edit_due' : edit_due,
            'active' : active,
            }
        return render_to_response(template, ctxt)

    except ObjectDoesNotExist:
        error = "That Membership does not appear to exist."
        return error_404(request, error)


def edit_due(request, membership, due=None):
    """ Add or edit a due """
    
    # Make sure that we are attempting to attach to a valid
    # membership.  

    try:
        membership = Membership.objects.get(id=membership)
    

    except ObjectDoesNotExist:
        error = "That Membership does not appear to exist"
        return error_404(request, error)
    
    # And make sure that we're looking up a valid due
    if due:
        due = int(due)
        try:
            due = Due.objects.get(id=due)
        
        except ObjectDoesNotExist:
            error = """ That due does not appear to exist."""
            return error_404(request, error)

    
    if request.method == 'POST':
        if due:
            # save changes to an existing due
            form = DueForm(request.POST, instance=due)
            if form.is_valid():
                due = form.save(commit=False)
                due.membership = membership
                due.save()
                form.save_m2m()
                return HttpResponseRedirect(
                    '/members/' + str(membership.id) + '/view/'
                    )

            else:
                template = 'edit_due.html'
                ctxt = { 
                    'request' : request,
                    'membership' : membership,
                    'form' : form
                    }
                return render_to_response(template, ctxt)

            
        else:
            # save a new due
            form = DueForm(request.POST)
            if form.is_valid():
                due = form.save(commit=False)
                due.membership = membership
                due.save()
                form.save_m2m()
                return HttpResponseRedirect(
                    '/members/' + str(membership.id) + '/view/'
                    )

            else:
                template = 'edit_due.html'
                ctxt = {
                    'request' : request,
                    'form' : form,
                    }
                return render_to_response(template, ctxt)

    else:
        # return a blank due form
        template = 'edit_due.html'
        ctxt = {
            'request' : request,
            'form' : DueForm(),
            }
        return render_to_response(template, ctxt)
            

def view_dues(request, membership):
    membership = int(membership)
    try: 
        membership = Membership.objects.get(id=membership)
        
    except ObjectDoesNotExist:
        error = "That Membership does not appear to exist."
        return error_404(request, error)

    dues = Due.objects.filter(membership=membership)

    template = 'view_dues.html'
    ctxt = {
        'request' : request,
        'dues' : dues,
        }
    return render_to_response(template, ctxt)

def membership_search(request):
    """ Search for a member.  Currently only searches by id """
    error = None
    membership_id = None

    if request.method == 'GET' and request.GET.has_key('membership_id'):
        membership_search = MembershipSearch(request.GET)
        if membership_search.is_valid():
            membership_id = request.GET.__getitem__('membership_id')

            try:
                membership = Membership.objects.get(id=membership_id)
                return HttpResponseRedirect(
                    '/members/' + str(membership_id) + '/view/'
                    )

            except ObjectDoesNotExist:
                error = """Membership #%s does not appear to exist.
""" % membership_id
        else:
            error = "Please enter a valid membership id number"

    else:
        error = "You did not specify a member to search for."

    template = "membership_search.html"
    ctxt = { 
            'request' : request, 
            'error' : error, 
            'membership_search' : MembershipSearch()
            }
    return render_to_response(template, ctxt)

        
    

            
            
        

