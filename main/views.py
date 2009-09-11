""" Views for Boston Mycological Club Website """

from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import Context, loader
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User, UserManager
from django.contrib.auth.decorators import (login_required, 
                                            user_passes_test, 
                                            permission_required)
import datetime
from bmc.settings import *
from models import (Announcement, Newsbit, PublicWalk, IDSession,
                    User, UserProfile, WalkArea, Walk,
                    Membership, Due)
from django import forms
from forms import (UserEditsUser, UserEditsProfile, 
                   UserEditsMembership, MembershipFetch,
                   EmailForm, WalkForm, WalkMushroomForm,
                   MembershipForm, UserForm, UserProfileForm,
                   DueForm, MembershipStatus, MembershipSearch,
                   WalkFormAdmin)

from django.core.mail import send_mail
from smtplib import SMTPException
from bmc.main.utilities import prev_next, unique
from mushroom_admin import *

"""----------------------------------------------------------------
                         Error Pages
----------------------------------------------------------------"""

def under_construction(request):
    """ Return a friendly under construction message. """
    template = 'under_construction.html'
    ctxt = { 'request' : request, 'media_url' : MEDIA_URL }
    return render_to_response(template, ctxt)

def error_404(request, error=None):
    """ Return a friendly '404' Error """
    if not error:
        error = "We can't find the page you requested."
    template = '404.html'
    ctxt = { 'request' : request, 'error' : error, 'media_url' : MEDIA_URL }
    return render_to_response(template, ctxt)

def halt(request, error=None):
    """ Display when the user is pokin' around some place they
    shouldn't be pokin'"""
    if not error:
        error = "You do not have permission to be here."
    template = 'halt.html'
    ctxt = { 'request' : request, 'error' : error, 'media_url' : MEDIA_URL }
    return render_to_response(template, ctxt)


"""----------------------------------------------------------------
                         Style Sheets
----------------------------------------------------------------"""


def style(request, sheet):
    """ Returns a cascading stylesheet. """
    template = sheet + '.css'
    ctxt = { 'media_url' : MEDIA_URL, }
    return render_to_response(template, ctxt, mimetype='text/css')



"""----------------------------------------------------------------
                         Public Pages
----------------------------------------------------------------"""

def index(request):
    """ Return our front page. """
    template = 'index.html'
    ctxt = {
        'announcements' : Announcement.objects.all()[:5],
        'newsbits' : Newsbit.objects.all()[:3],
        'media_url' : MEDIA_URL,
        'request' : request,
        'page_name' : 'Home',
        }
    return render_to_response(template, ctxt)

def about(request):
    template = 'about.html'
    ctxt = { 
        'request' : request, 
        'page_name' : 'About Us',
        'media_url' : MEDIA_URL,
        }
    return render_to_response(template, ctxt)

def application(request):
    template = 'application.html'
    ctxt = { 
        'request' : request, 
        'page_name' : 'Application', 
        'media_url' : MEDIA_URL,
        }
    return render_to_response(template, ctxt)

def schedule(request):
    """ Displays the clubs schedule of activities. """
    template = 'schedule.html'

    walks_in_area = []
    public_walks = Walk.objects.filter(
        public=True,
        date__gte=datetime.date.today(),
        )
    id_sessions = IDSession.objects.filter(
        when__gte=datetime.date.today()
        )

    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(
                user=request.user.id
                )
            areas = user_profile.areas.all()
            walks_in_area = []
            for area in areas:
                walks_in_area.append(
                    Walk.objects.filter(
                            areas=area,
                            date__gte=datetime.date.today(),
                            )
                    )
        except ObjectDoesNotExist:
            pass

    ctxt = {
        'public_walks' : public_walks,
        'id_sessions' : id_sessions,
        'media_url' : MEDIA_URL,
        'request' : request,
        'walks_in_area' : walks_in_area,
        'page_name' : 'Schedule',
        }
    return render_to_response(template, ctxt)

def page(request, page):
    """ Given the page name, return the page. """
    template = page + '.html'
    ctxt = {
        'media_url' : MEDIA_URL,
        'request' : request,
        'page_name' : page,
        }
    return render_to_response(template, ctxt)

def story(request, year, month, day, time):
    """ Fetch a story page, identified by timestamp
    """
    ts = year + "-" + month + "-" + day + " " + time

    from django.core.exceptions import ObjectDoesNotExist

    try: 
        story = Announcement.objects.get(timestamp=ts)
        template = "story.html"
        ctxt = {
            'heading' : story.heading,
            'summary' : story.summary,
            'full_story' : story.full_story,
            'ts' : story.timestamp,
            'request' : request,
            'page_name' : story.heading,
            'media_url' : MEDIA_URL,
            }

        return render_to_response(template, ctxt)    

    except ObjectDoesNotExist:
        error = "We couldn't find a story with that timestamp."
        return error_404(request, error)


"""----------------------------------------------------------------
                         User Profile Tools
----------------------------------------------------------------"""

@login_required(redirect_field_name='redirect_to')
def profile(request):
    """ User Profile Page """

    try:
        user = User.objects.get(id=request.user.id)
        user_profile = UserProfile.objects.get(user=user.id)
        membership = Membership.objects.get(id=user_profile.membership.id)

    except ObjectDoesNotExist:
        if request.user.is_superuser:
            # Hacky fix to take superusers w/out a profile to the
            # right place
            return HttpResponseRedirect('/mushroom_admin/')

        else:
            error = "We cannot find you user profile. "
            error += "Please contact the BMC admin."
            return error_404(request, error)
    
    # Pull up list of walks in the users' area
    areas = user_profile.areas.all()
    walks_in_area = []
    for area in areas:
        walks_in_area += Walk.objects.filter(
            areas=area,
            date__gte=datetime.date.today()
            )

    # Eliminate duplicate entries
    walks_in_area=unique(walks_in_area)
     
    template = 'profile.html'
    ctxt = { 
        'request' : request, 
        'walks_in_area' : walks_in_area,
        'user' : user,
        'user_profile' : user_profile,
        'membership' : membership,
        'forms' : forms,
        'page_name' : 'Profile',
        'media_url' : MEDIA_URL,
        }
    return render_to_response(template, ctxt)

@login_required(redirect_field_name='redirect_to')
def edit_profile(request):
    """ Allows a user to edit limited information about their
    username, membership, and user profile. """

    try:
        user = User.objects.get(id=request.user.id)
        user_profile = UserProfile.objects.get(user=user.id)
        membership = Membership.objects.get(id=user_profile.membership.id)

    except ObjectDoesNotExist:
        error = "We cannot find you user profile. "
        error += "Please contact the BMC admin."
        return error_404(request, error)

    if request.method == 'POST':
        edit_user = UserEditsUser(request.POST, instance=user)
        edit_profile = UserEditsProfile(request.POST, 
                                        instance=user_profile)
        edit_membership = UserEditsMembership(request.POST, 
                                              instance=membership)
        if (edit_user.is_valid() and edit_profile.is_valid() and 
            edit_membership.is_valid()):
            edit_user.save()
            edit_profile.save()
            edit_membership.save()
            return HttpResponseRedirect('/accounts/profile/')
        else:
            forms = (
                UserEditsUser(request.POST),
                UserEditsProfile(request.POST),
                UserEditsMembership(request.POST),
                )
            template = 'edit_profile.html'
            ctxt = { 
                'forms' : forms, 
                'request' : request, 
                'page_name' : 'Edit Profile',
                'media_url' : MEDIA_URL,
                }
            return render_to_response(template, ctxt)

    else:
        forms = (
            UserEditsUser(instance=user),
            UserEditsProfile(instance=user_profile),
            UserEditsMembership(instance=membership),
            )
        template = 'edit_profile.html'
        ctxt = { 
            'forms' : forms, 
            'request' : request,
            'page_name' : 'Edit Profile',
            'media_url' : MEDIA_URL,
            }
        return render_to_response(template, ctxt)


"""----------------------------------------------------------------
                         Walk Tools 
----------------------------------------------------------------"""

@login_required(redirect_field_name='redirect_to')
def list_walks(request, start=None, per_page=None):
    """ Lists all walks. """

    pn = prev_next(start, per_page)
    walk_list = Walk.objects.all()[pn.start:pn.next]
    if pn.per_page > len(walk_list): pn.next = 0  

    template = 'walk_list.html'
    ctxt = { 
        'request' : request,
        'walk_list' : walk_list, 
        'prev_next' : pn,
        'page_name' : 'Walk List',
        'media_url' : MEDIA_URL,
        }
    return render_to_response(template, ctxt)

@login_required(redirect_field_name='redirect_to')
def view_walk(request, walk=None):
    """ View details about a specific walk. """

    if not walk:
        error = "Please specify a walk to view"
        return error_404(request, error)

    try: 
        walk = Walk.objects.get(id=walk)

        # Decide whether user has permission to view 'edit' link
        permission = False
        if request.user.id == walk.creator.id: permission = True

        template = "walk.html"
        ctxt = { 
            'walk' : walk, 
            'request' : request, 
            'permission' : permission,
            'page_name' : 'Walk',
            'media_url' : MEDIA_URL,
            }
        return render_to_response(template, ctxt)

    except:
        error = "It appears that the walk you requested does not exist."
        return error_404(request, error)

@login_required(redirect_field_name='redirect_to')
def create_walk(request):
    """ View to create a new walk.  """

    # Give our admins a Walk Form w/ added features
    if request.user.is_superuser: WalkForm = WalkFormAdmin
    else: from forms import WalkForm

    if request.method == 'POST':
        form = WalkForm(request.POST)
        if form.is_valid():
            walk = form.save(commit=False)
            walk.creator = request.user
            walk.save()
            form.save_m2m()

            return HttpResponseRedirect(reverse(profile))
                
        else:
            form = WalkForm(request.POST)
            template = 'edit_walk.html'
            ctxt = { 
                'form' : form,  
                'request' : request, 
                'page_name' : 'Create Walk',
                'media_url' : MEDIA_URL,
                }
            return render_to_response(template, ctxt)

    else:
        form = WalkForm(initial={ 
                'creator' : User.objects.get(username=request.user).id
                })
        template = 'edit_walk.html'
        ctxt = { 
            'form' : form,  
            'request' : request, 
            'walk' : None,
            'page_name' : 'Create Walk',
            'media_url' : MEDIA_URL,
            }
        return render_to_response(template, ctxt)

@login_required(redirect_field_name='redirect_to')
def edit_walk(request, walk=None):
    """ Edit an existing walk. """

    # Give our admins a Walk Form w/ added features
    if request.user.is_superuser: WalkForm = WalkFormAdmin
    else: from forms import WalkForm

    if not walk:
        return create_walk(request)

    try:
        walk = Walk.objects.get(id=walk)
        if request.user.id != walk.creator.id:
            if not request.user.is_superuser:
                error = "You do not have permission to edit this walk."
                return halt(request, error)

    except ObjectDoesNotExist:
        error = "That walk does not appear to exist"
        return error_404(request, error)

    if request.method == 'POST':

        form = WalkForm(request.POST, instance=walk)

        if form.is_valid():
            walk = form.save()
            return HttpResponseRedirect(reverse(profile))

        else:
            form = WalkForm(request.POST)
            template = 'edit_walk.html'
            ctxt = { 
                'form' : form, 
                'request' : request,
                'page_name' : 'Edit Walk',
                'media_url' : MEDIA_URL,
                }
            return render_to_response(template, ctxt)

    else:
        form = WalkForm(instance=walk)
        template = 'edit_walk.html'
        ctxt = { 
            'form' : form,  
            'request' : request,
            'walk' : walk,
            'page_name' : 'Edit Walk',
            'media_url' : MEDIA_URL,
            }
        return render_to_response(template, ctxt)


@login_required(redirect_field_name='redirect_to')
def mushrooms(request, walk=None):
    if not walk:
        error = "Please specify a walk"
        return error_404(request, error)

    try:
        walk = Walk.objects.get(id=walk)
        
    except ObjectDoesNotExist:
        error = "That walk does not appear to exist"
        return error_404(request, error)

    if request.method == 'POST':
        
        form = WalkMushroomForm(request.POST, instance=walk)

        if form.is_valid():
            walk = form.save()
            return HttpResponseRedirect(
                '/walks/view/' + str(walk.id) + '/'
                )

        else:
            form = WalkMushroomForm(request.POST)

    else:
        form = WalkMushroomForm(instance=walk)


    template = 'walk_mushrooms.html'
    ctxt = { 
        'form' : form, 
        'request' : request, 
        'walk' : walk,
        'page_name' : 'Mushrooms',
        'media_url' : MEDIA_URL,
        }
    return render_to_response(template, ctxt)

"""----------------------------------------------------------------
                         Membership Tools

Note:  These tools need to get folded into generic "mushroom admin"
       views at some point.  
----------------------------------------------------------------"""

@user_passes_test(
    lambda u: u.has_perm('u.is_superuser'),
    login_url = '/halt/')
def list_memberships(request, start=None, per_page=None, 
                     due_by=None, year=None, month=None):
    """ List all memberships, or all late memberships. """


    pn = prev_next(start, per_page)
    if due_by:
        if month and year:
            due_by = datetime.date(int(year), int(month), 1)
        else:
            due_by = datetime.date.today()
            
        members = Membership.objects.exclude(
            due__paid_thru__gte=due_by,
            ).exclude(
                membership_type='honorary'
                ).exclude(
                    membership_type__startswith='corresponding'
                    )[pn.start:pn.next]
            
    else:
        members = Membership.objects.all()[pn.start:pn.next]
        due_by = None

    if pn.per_page > len(members): pn.next = 0  
    
    member_list = []
    for member in members:
        users = User.objects.filter(
            userprofile__membership=member.id)
        mem_blob = { 'membership' : member, 'users' : users }
        member_list.append(mem_blob)

    template = 'memberlist.html'
    ctxt = { 
        'member_list' : member_list, 
        'request' : request,
        'due_by' : due_by,
        'prev_next' : pn,
        'page_name' : 'List Memberships',
        'media_url' : MEDIA_URL,
        }
    return render_to_response(template, ctxt)


@user_passes_test(
    lambda u: u.has_perm('u.is_superuser'),
    login_url = '/halt/')
def view_membership(request, membership=None):
    """ View Details of a Membership """

    if not membership:
        error = "Please specify a membership to view."
        return error_404(request, error)

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
            'page_name' : 'Membership',
            'media_url' : MEDIA_URL,
            }
        return render_to_response(template, ctxt)

    except ObjectDoesNotExist:
        error = "That Membership does not appear to exist."
        return error_404(request, error)

@user_passes_test(
    lambda u: u.has_perm('u.is_superuser'),
    login_url = '/halt/')
def edit_membership(request, membership=None):
    """ Edit an existing membership, or add a new membership if none
    specified."""

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
                    '/memberships/' + str(membership.id) + '/view/'
                    )

            else:
                form = MembershipForm(request.POST)
                template = 'edit_membership.html'
                ctxt = { 
                    'form' : form, 
                    'request' : request, 
                    'membership' : membership,
                    'page_name' : 'Edit Membership', 
                    'media_url' : MEDIA_URL,
                    }
                return render_to_response(template, ctxt)

        else:
            # save a new membership
            form = MembershipForm(request.POST)
            if form.is_valid():
                membership = form.save()
                return HttpResponseRedirect(
                    '/memberships/' + str(membership.id) + '/view/'
                    )

            else:
                form = MembershipForm(request.POST)
                template = 'edit_membership.html'
                ctxt = { 
                    'form' : form, 
                    'request' : request, 
                    'membership' : membership,
                    'page_name' : 'Create Membership',
                    'media_url' : MEDIA_URL,
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
            'page_name' : 'Edit Membership',
            'media_url' : MEDIA_URL,
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
            'page_name' : 'Create Membership',
            'media_url' : MEDIA_URL,
            }
        return render_to_response(template, ctxt)

@user_passes_test(
    lambda u: u.has_perm('u.is_superuser'),
    login_url = '/halt/')
def create_membership(request):
    edit_membership(request, membership=None)

@user_passes_test(
    lambda u: u.has_perm('u.is_superuser'),
    login_url = '/halt/')
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
                user = user_form.save()
                profile = profile_form.save()

                return HttpResponseRedirect(
                    '/memberships/' + str(membership.id) + '/view/'
                    )
            else:
                template = 'edit_user.html'
                ctxt = { 
                    'request' : request, 
                    'membership' : membership,
                    'user' : user.id,
                    'edit_user' : user_form,
                    'edit_profile' : profile_form,
                    'page_name' : 'Edit User',
                    'media_url' : MEDIA_URL,
                    }
                return render_to_response(template, ctxt)


        else:
            # save a new user
            user_form = UserForm(request.POST)
            profile_form = UserProfileForm(request.POST)
            if user_form.is_valid() and profile_form.is_valid():
                user = user_form.save()
                profile = profile_form.save(commit=False)
                profile.user = User.objects.get(id=user.id)
                profile.membership = membership
                profile.save()
                profile_form.save_m2m()

#               try:
                # Try to send an email w/ password reset link to
                # the user
                subject = "Boston Mycological Club Account "
                subject += "Created"
                email_template = 'registration/new_user_email.html'
                ctxt = { 'user' : user, 'media_url' : MEDIA_URL, }
                message = loader.get_template(email_template)
                message = message.render(Context(ctxt))

                send_mail(subject, message, SERVER_EMAIL, 
                          [user.email], fail_silently=False,
                          )
#                except:
#                    error = "Account created, but email was not sent"
#                    return error_404(request, error)

                return HttpResponseRedirect(
                    '/memberships/' + str(membership.id) + '/view/'
                    )
                

            else:
                template = 'edit_user.html'
                ctxt = { 
                    'request' : request, 
                    'membership' : membership,
                    'user' : None,
                    'edit_user' : user_form,
                    'edit_profile' : profile_form,
                    'page_name' : 'Create User',
                    'media_url' : MEDIA_URL,
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
            'page_name' : 'Edit User',
            'media_url' : MEDIA_URL,
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
            'page_name' : 'Create User',
            'media_url' : MEDIA_URL,
            }
        return render_to_response(template, ctxt)

        
@user_passes_test(
    lambda u: u.has_perm('u.is_superuser'),
    login_url = '/halt/')
def membership_status(request, membership, action):
    """ Suspend a membership, or restore a suspended account. """
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
        profiles = []
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
            '/memberships/' + str(membership.id) + '/view/'
            )

    else:
        status = True
        if action == 'suspend': status = False

        template = "membership_status.html"
        ctxt = { 
            'request' : request, 
            'status' : status,
            'form' : MembershipStatus(),
            'membership' : membership,
            'page_name' : 'Change Membership Status',
            'profiles' : profiles,
            'media_url' : MEDIA_URL,
            }
        return render_to_response(template, ctxt)

@user_passes_test(
    lambda u: u.has_perm('u.is_superuser'),
    login_url = '/halt/')
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
                    '/memberships/' + str(membership.id) + '/view/'
                    )

            else:
                template = 'edit_due.html'
                ctxt = { 
                    'due' : due,
                    'request' : request,
                    'membership' : membership,
                    'form' : form,
                    'page_name' : 'Edit Due',
                    'media_url' : MEDIA_URL,
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
                    '/memberships/' + str(membership.id) + '/view/'
                    )

            else:
                template = 'edit_due.html'
                ctxt = {
                    'request' : request,
                    'form' : form,
                    'membership' : membership,
                    'page_name' : 'Add Due',
                    'media_url' : MEDIA_URL,
                    }
                return render_to_response(template, ctxt)

    else:
        if due:
            template = 'edit_due.html'
            ctxt = {
                'request' : request,
                'form' : DueForm(instance=due),
                'due' : due,
                'membership' : membership,
                'page_name' : 'Edit Due',
                'media_url' : MEDIA_URL,
                }
            return render_to_response(template, ctxt)

        else:
            # return a blank due form
            template = 'edit_due.html'
            ctxt = {
                'request' : request,
                'form' : DueForm(),
                'membership' : membership,
                'page_name' : 'Add Due',
                'media_url' : MEDIA_URL,
                }
            return render_to_response(template, ctxt)
            

@user_passes_test(
    lambda u: u.has_perm('u.is_superuser'),
    login_url = '/halt/')
def view_dues(request, membership=None):
    """ View a list of dues associated with a membership."""
    if not membership:
        error = "Plesae specify and membership"
        return error_404(request, error)

    membership = int(membership)
    try: 
        membership = Membership.objects.get(id=membership)
        
    except ObjectDoesNotExist:
        error = "That Membership does not appear to exist."
        return error_404(request, error)

    dues = Due.objects.filter(membership=membership)[:25]

    template = 'view_dues.html'
    ctxt = {
        'request' : request,
        'dues' : dues,
        'membership' : membership,
        'page_name' : 'View Dues',
        'media_url' : MEDIA_URL,
        }
    return render_to_response(template, ctxt)

@user_passes_test(
    lambda u: u.has_perm('u.is_superuser'),
    login_url = '/halt/')
def membership_search(request):
    member_list = []

    if request.GET.has_key('last_name'):
        membership_search = MembershipSearch(request.GET)
        if membership_search.is_valid():
            memberships = Membership.objects.filter(
                userprofile__user__last_name__icontains=request.GET.__getitem__('last_name')
                )[:25]
            if len(memberships) == 1:
                return HttpResponseRedirect(
                    '/memberships/' + str(memberships[0].id) + '/view/'
                    )
                
            for membership in memberships:
                users = User.objects.filter(
                    userprofile__membership=membership.id
                    )
                mem_blob = { 
                    'membership' : membership, 
                    'users' : users,
                    }
                member_list.append(mem_blob)

        template = 'membership_search.html'
        ctxt = { 
            'request' : request, 
            'memberships' : memberships,
            'membership_search' : membership_search,
            'member_list' : member_list,
            'media_url' : MEDIA_URL,
            }
        return render_to_response(template, ctxt)
            

@user_passes_test(
    lambda u: u.has_perm('u.is_superuser'),
    login_url = '/halt/')
def membership_fetch(request):
    """ Fetch a Member by Membership ID """
    error = None
    membership_id = None

    if request.method == 'GET' and request.GET.has_key('membership_id'):
        membership_fetch = MembershipFetch(request.GET)
        if membership_fetch.is_valid():
            membership_id = request.GET.__getitem__('membership_id')

            try:
                membership = Membership.objects.get(id=membership_id)
                return HttpResponseRedirect(
                    '/memberships/' + str(membership_id) + '/view/'
                    )

            except ObjectDoesNotExist:
                error = """Membership #%s does not appear to exist.
""" % membership_id
        else:
            error = "Please enter a valid membership id number"

    else:
        error = "You did not specify a member to search for."

    template = "membership_fetch.html"
    ctxt = { 
            'request' : request, 
            'error' : error, 
            'membership_fetch' : MembershipFetch(),
            'page_name' : 'Search Error',
            'media_url' : MEDIA_URL,
            }
    return render_to_response(template, ctxt)

"""----------------------------------------------------------------
                         Mushroom Admin and Other Tools
----------------------------------------------------------------"""

@user_passes_test(
    lambda u: u.has_perm('u.is_superuser'),
    login_url = '/halt/')
def mushroom_admin(request):
    """ Pulls up an custom admin page for the site."""
    membership_fetch = MembershipFetch()
    membership_search = MembershipSearch()

    # Fetch dates of "due_by by" list
    today = datetime.date.today()
    next_month = today.month + 1
    nm_year = today.year
    may_year = today.year

    if next_month > 12:  
        next_month = 1
        mm_year += 1

    may_year = today.year
    if today.month > 5:
        may_year += 1
        

    template = 'mushroom_admin.html'
    ctxt = { 
        'request' : request, 
        'membership_fetch' : membership_fetch,
        'membership_search' : membership_search,
        'next_month' : next_month,
        'nm_year' : nm_year,
        'may_year' : may_year,
        'today' : today,
        'page_name' : 'Mushroom Admin',
        'media_url' : MEDIA_URL,
        }
    return render_to_response(template, ctxt)

@user_passes_test(
    lambda u: u.has_perm('u.is_superuser'),
    login_url = '/halt/')
def mushroom_admin_list(request, entries, start=None, per_page=None):
    """ List a series of entries for one model in the mushroom_admin
    page. """

    entries = globals()[entries]() # Not sure if this is the most
                                   # efficient way to do this (using
                                   # eval might almost be okay,
                                   # because we're only accepting a
                                   # regular expression matching
                                   # [a-z]+ as input for 'entries'
                                   # ... but paranoia is good, right?)
    model = entries.MODEL
    entry_name = entries.NAME
    template = entries.LIST_TEMPLATE

    pn = prev_next(start, per_page)

    entries = model.objects.all()[pn.start:pn.next]
    if pn.per_page > len(entries): pn.next = 0

    ctxt = {
        'entries' : entries,
        'request' : request,
        'prev_next' : pn,
        'page_name' : "%ss" % entry_name,
        'entry_name' : entry_name,
        'media_url' : MEDIA_URL,
        }
    return render_to_response(template, ctxt)


@user_passes_test(
    lambda u: u.has_perm('u.is_superuser'),
    login_url = '/halt/')
def mushroom_admin_view(request, entries, entry_id):
    entries = globals()[entries]()
    entry_name = entries.NAME
    model = entries.MODEL
    template = entries.VIEW_TEMPLATE
    entry_id = int(entry_id)
    permission = entries.edit_permission()

    if not entry_id:
        error = "Please specify a %s to view" % entry_name
        return error_404(request, error)

    try:
        entry = model.objects.get(id=entry_id)

    except:
        error = "I could not find that %s" % entry_name
        return error_404(request, error)

    ctxt = {
        'entry' : entry,
        'entry_name' : entry_name,
        'entry_id' : entry_id,
        'page_name' : entry_name,
        'request' : request,
        'permission' : permission,
        'media_url' : MEDIA_URL,
        }

    return render_to_response(template, ctxt)

@user_passes_test(
    lambda u: u.has_perm('u.is_superuser'),
    login_url = '/halt/')
def mushroom_admin_edit(request, entries, entry_id=None,):
    """ Edit an entry, or create a new entry, if no entry specified
    """

    entry = ''
    entries = globals()[entries]()
    entry_name = entries.NAME
    model = entries.MODEL
    template = entries.EDIT_TEMPLATE
    if entry_id: entry_id = int(entry_id)
    form = entries.FORM

    # Fetch an entry object, if we specified an entry.
    if entry_id:
        entry_id = int(entry_id)
        try:
            entry = model.objects.get(id=entry_id)

        except ObjectDoesNotExist:
            error = """That %s does not appear to exist in the database.
                    """ % entry_name
            return error_404(request, error)

    # Attempt to save our entry.  
    if request.method == 'POST':
        if entry: form = form(request.POST, instance=entry)
        else: form = form(request.POST)

        if form.is_valid():
            form = form.save()
            return HttpResponseRedirect(
                '/mushroom_admin/%ss/' % entry_name
                )

        else:
            form = form(request.POST)
            # renders below
            
    # Return a blank form, or a form with errors if we didn't specify
    # an object to save, or if we tried to save an invalid form.
    else:
        if entry: form = form(instance=entry)
        else: form = form()

    if entry: page_name = 'Edit' 
    else: page_name = 'Create'

    ctxt = {
        'form' : form,
        'request' : request,
        'entry' : entry,
        'model' : model,
        'page_name' : page_name,
        'entry_id' : entry_id,
        'entry_name' : entry_name,
        'media_url' : MEDIA_URL,
        }
    return render_to_response(template, ctxt)


"""----------------------------------------------------------------
                         Email Tools
----------------------------------------------------------------"""

@user_passes_test(
    lambda u: u.has_perm('u.is_superuser'),
    login_url = '/halt/')
def list_emails(request):
    """ List all user emails. """
    try:
        users = User.objects.all()
    except ObjectDoesNotExist:
        error = "Couldn't fetch a list of users!"
        return error_404(request, error)
    
    template='list_emails.html'
    ctxt = { 
        'request' : request, 
        'users' : users, 
        'page_name' : 'Email List', 
        'media_url' : MEDIA_URL,
        }
    return render_to_response(template, ctxt)

@user_passes_test(
    lambda u: u.has_perm('u.is_superuser'),
    login_url = '/halt/')
def sent_email(request, send_errors=None):
    """ Return a page confirming a sent email """
    template = 'sent_email.html'
    ctxt = { 'request' : request,
             'send_errors' : send_errors,
             'page_name' : 'Sent Email',
             'media_url' : MEDIA_URL,
             }
    return render_to_response(template, ctxt)
                 
@user_passes_test(
    lambda u: u.has_perm('u.is_superuser'),
    login_url = '/halt/')
def send_email(request, sent=None):
    """ Send an email to all club members. """

    form = EmailForm()
    template='send_email.html'
    users = []
    send_errors = []

    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            form = form.cleaned_data
            subject = form['subject']
            message = form['message']

            try:
                users = User.objects.filter(
                        is_active=True,
                        userprofile__want_email=True,
                        )
            except ObjectDoesNotExist:
                error = "Can't pull up the user list!"
                return error_404(request, error)

            for user in users:
                try:
                    user_email = user.email
                    send_mail(subject, 
                              message, 
                              SERVER_EMAIL,
                              [user_email],
                              fail_silently=False,
                              )
                except SMTPException:
                    # Need to grab Exception and pass it to template
                    error = "There was an error sending mail!"
                    return error_404(request, error)

                except:
                    error = "There was an error sending mail!"
                    return error_404(request, error)

            return HttpResponseRedirect(reverse(sent_email))

        else:
            form = EmailForm(request.POST)
            
    ctxt = { 
        'request' : request, 
        'form' : form, 
        'users' : users,
        'page_name' : 'Email All Members',
        'media_url' : MEDIA_URL,
        }
    return render_to_response(template, ctxt)
        
