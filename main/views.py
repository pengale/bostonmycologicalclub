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
                   UserEditsMembership, MembershipSearch,
                   EmailForm, WalkForm, WalkMushroomForm,
                   MembershipForm, UserForm, UserProfileForm,
                   DueForm, MembershipStatus, MembershipSearch)

from django.core.mail import send_mail
from smtplib import SMTPException
from bmc.main.utilities import prev_next

"""----------------------------------------------------------------
                         Error Pages
----------------------------------------------------------------"""

def under_construction(request):
    """ Return a friendly under construction message. """
    template = 'under_construction.html'
    ctxt = { 'request' : request, }
    return render_to_response(template, ctxt)

def error_404(request, error=None):
    """ Return a friendly '404' Error """
    if not error:
        error = "We can't find the page you requested."
    template = '404.html'
    ctxt = { 'request' : request, 'error' : error }
    return render_to_response(template, ctxt)

def halt(request, error=None):
    """ Display when the user is pokin' around some place they
    shouldn't be pokin'"""
    if not error:
        error = "You do not have permission to be here."
    template = 'halt.html'
    ctxt = { 'request' : request, 'error' : error }
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
        'announcements' : Announcement.objects.all(),
        'newsbits' : Newsbit.objects.all(),
        'media_url' : MEDIA_URL,
        'request' : request,
        }
    return render_to_response(template, ctxt)

def schedule(request):
    """ Displays the clubs schedule of activities. """
    template = 'ClubActivities.html'

    walks_in_area = []
    public_walks = PublicWalk.objects.filter(
        when__gte=datetime.date.today()
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
        }
    return render_to_response(template, ctxt)

def page(request, page):
    """ Given the page name, return the page. """
    template = page + '.html'
    ctxt = {
        'media_url' : MEDIA_URL,
        'request' : request,
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
            }

        return render_to_response(template, ctxt)    

    except ObjectDoesNotExist:
        template = "error.html"
        ctxt = { 'request' : request }

        return render_to_response(template, ctxt)    


"""----------------------------------------------------------------
                         User Profile Tools
----------------------------------------------------------------"""

@login_required(redirect_field_name='redirect_to')
def profile(request):
    """ User Profile Page """

    try:
        user = User.objects.get(id=request.user.id)
        user_profile = UserProfile.objects.get(user=user.id)
        membership = Membership.objects.get(id=1)

    except ObjectDoesNotExist:
        if request.user.is_superuser:
            # Hacky fix to take superusers w/out a profile to the
            # right place
            return HttpResponseRedirect('/mushroom_admin/')

        else:
            error = "We cannot find you user profile. "
            error += "Please contact the BMC admin."
            return error_404(request, error)
    
    areas = user_profile.areas.all()
    walks_in_area = []
    for area in areas:
        walks_in_area.append(Walk.objects.filter(
                areas=area,
                date__gte=datetime.date.today()
                ))
     
    template = 'profile.html'
    ctxt = { 
        'request' : request, 
        'walks_in_area' : walks_in_area,
        'user' : user,
        'user_profile' : user_profile,
        'membership' : membership,
        'forms' : forms,
        }
    return render_to_response(template, ctxt)

@login_required(redirect_field_name='redirect_to')
def edit_profile(request):
    """ Allows a user to edit limited information about their
    username, membership, and user profile. """
    try:
        user = User.objects.get(id=request.user.id)
        user_profile = UserProfile.objects.get(user=user.id)
        membership = Membership.objects.get(id=1)

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
            user = edit_user.save(commit=False)
            user.email = user.username
            user.save()
            edit_user.save_m2m()
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
            ctxt = { 'forms' : forms, 'request' : request }
            return render_to_response(template, ctxt)

    else:
        forms = (
            UserEditsUser(instance=user),
            UserEditsProfile(instance=user_profile),
            UserEditsMembership(instance=membership),
            )
        template = 'edit_profile.html'
        ctxt = { 'forms' : forms, 'request' : request }
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
        'prev_next' : pn
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
            'permission' : permission 
            }
        return render_to_response(template, ctxt)

    except:
        error = "It appears that the walk you requested does not exist."
        template = "404.html"
        ctxt = { "error" : error, 'request' : request }
        return render_to_response(template, ctxt)

@login_required(redirect_field_name='redirect_to')
def create_walk(request):
    """ View to create a new walk.  """

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
            ctxt = { 'form' : form,  'request' : request }
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
            }
        return render_to_response(template, ctxt)

@login_required(redirect_field_name='redirect_to')
def edit_walk(request, walk=None):
    """ Edit an existing walk. """
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
            walk = form.save(commit=False)
            walk.creator = request.user
            walk.save()
            form.save_m2m()
            return HttpResponseRedirect(reverse(profile))

        else:
            form = WalkForm(request.POST)
            template = 'edit_walk.html'
            ctxt = { 'form' : form, 'request' : request }
            return render_to_response(template, ctxt)

    else:
        form = WalkForm(instance=walk)
        template = 'edit_walk.html'
        ctxt = { 
            'form' : form,  
            'request' : request,
            'walk' : walk,
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
    ctxt = { 'form' : form, 'request' : request, 'walk' : walk }
    return render_to_response(template, ctxt)

"""----------------------------------------------------------------
                         Membership Tools
----------------------------------------------------------------"""

@user_passes_test(
    lambda u: u.has_perm('u.is_superuser'),
    login_url = '/halt/')
def list_memberships(request, start=None, per_page=None, 
                     due_by=None, year=None, month=None):
    """ List all memberships, or all late memberships. """

    if request.method=='GET' and due_by:
        pn = None
        if month and year:
            due_by = datetime.date(int(year), int(month), 1)
        else:
            due_by = datetime.date.today()
            
        members = Membership.objects.all()
        due_by_members = []
        for member in members:
            try:
                dues = Due.objects.filter(
                    membership=member.id,
                    paid_thru__gte=due_by,
                    )
                if not dues:  due_by_members.append(member)            

            except ObjectDoesNotExist:
                due_by_members.append(member)

        members = due_by_members                

    else:
        pn = prev_next(start, per_page)
        members = Membership.objects.all()[pn.start:pn.next]
        if pn.per_page > len(members): pn.next = 0  
        due_by = None
    
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
                    'membership' : membership 
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
                user = user_form.save(commit=False)
                user.email = user.username
                user.save()
                user_form.save_m2m()
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

 #               try:
                # Try to send an email w/ password reset link to
                # the user
                subject = "Boston Mycological Club Account "
                subject += "Created"
                email_template = 'registration/new_user_email.html'
                ctxt = { 'user' : user }
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
                    '/memberships/' + str(membership.id) + '/view/'
                    )

            else:
                template = 'edit_due.html'
                ctxt = {
                    'request' : request,
                    'form' : form,
                    }
                return render_to_response(template, ctxt)

    else:
        if due:
            # return a blank due form
            template = 'edit_due.html'
            ctxt = {
                'request' : request,
                'form' : DueForm(instance=due),
                'due' : due,
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

    dues = Due.objects.filter(membership=membership)

    template = 'view_dues.html'
    ctxt = {
        'request' : request,
        'dues' : dues,
        'membership' : membership,
        }
    return render_to_response(template, ctxt)

@user_passes_test(
    lambda u: u.has_perm('u.is_superuser'),
    login_url = '/halt/')
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
                    '/memberships/' + str(membership_id) + '/view/'
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

@user_passes_test(
    lambda u: u.has_perm('u.is_superuser'),
    login_url = '/halt/')
def mushroom_admin(request):
    """ Pulls up an custom admin page for the site."""
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
        'membership_search' : membership_search,
        'next_month' : next_month,
        'nm_year' : nm_year,
        'may_year' : may_year,
        'today' : today,
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
    ctxt = { 'request' : request, 'users' : users }
    return render_to_response(template, ctxt)

@user_passes_test(
    lambda u: u.has_perm('u.is_superuser'),
    login_url = '/halt/')
def sent_email(request, send_errors=None):
    """ Return a page confirming a sent email """
    template = 'sent_email.html'
    ctxt = { 'request' : request,
             'send_errors' : send_errors,
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
                    # Need to come up with a good way to display these
                    # errors.  Not sure if possible to pass through a
                    # redirect.
                    send_error = 'error sending to %s' % user_email
                    send_errors.append(send_error)

            return HttpResponseRedirect(reverse(sent_email))

        else:
            form = EmailForm(request.POST)
            
    ctxt = { 
        'request' : request, 
        'form' : form, 
        'users' : users,
        }
    return render_to_response(template, ctxt)
        
