""" Views for Boston Mycological Club Website """

from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
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
                   EmailForm)
from django.core.mail import send_mail
from smtplib import SMTPException

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

    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(
                user=request.user.id
                )
            areas = user_profile.areas.all()
            walks_in_area = []
            for area in areas:
                walks_in_area.append(
                    Walk.objects.filter(areas=area)
                    )
        except ObjectDoesNotExist:
            pass

    ctxt = {
        'public_walks' : PublicWalk.objects.all(),
        'id_sessions' : IDSession.objects.all(),
        'media_url' : MEDIA_URL,
        'request' : request,
        'walks_in_area' : walks_in_area,
        }
    return render_to_response(template, ctxt)

def under_construction(request):
    """ Return a friendly under construction message. """
    template = 'under_construction.html'
    ctxt = { 'request' : request, }
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

def style(request, sheet):
    """ Returns a cascading stylesheet. """
    template = sheet + '.css'
    ctxt = { 'media_url' : MEDIA_URL, }
    return render_to_response(template, ctxt, mimetype='text/css')

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

@login_required(redirect_field_name='redirect_to')
def walks(request, action, walk):
    """ If the user wants to edit, create, list, or view walks, 
    call the appropriate function from walk_tools.py. """
    from walk_tools import *

    if action == "list" : return view_walklist(request)
    if action == "view" :  return view_walk(request, walk)
    if action == "create" :  return create_walk(request)
    if action == "edit" :  return edit_walk(request, walk)
    if action == "done" :  return made_walk(request, walk)
    if action == "mushrooms" :  return mushrooms(request, walk)

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
        walks_in_area.append(Walk.objects.filter(areas=area))

     
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

@user_passes_test(
    lambda u: u.has_perm('u.is_superuser'),
    login_url = '/halt/')
def memberships(request, action, membership=None, criteria=None):
    """ Membership manipulation tools """

    from membership_tools import *
    
    if action == "list" : return list_memberships(
        request, criteria)
    if action == "edit" : return edit_membership(
        request, membership)
    if action == "view" : return view_membership(
        request, membership)
    if action == "status" : return membership_status(
        request, membership, criteria)
    if action == "dues" : return view_dues(
        request, membership)
    if action == "edit_user" : return edit_user(
        request, membership, criteria)
    if action == "edit_due" : return edit_due(
        request, membership, criteria)
    if action == "search" : return membership_search(request)

@user_passes_test(
    lambda u: u.has_perm('u.is_superuser'),
    login_url = '/halt/')
def memberships_due(request, year, month):
    """ Get overdue memberships """
    
    memberships = Membership.objects.all()
    due_memberships = []
    for membership in memberships:
        try:
            dues = Due.objects.filter(membership=membership.id)[:1]
        except ObjectDoesNotExist:
            pass

    template = "memberships_due.html"
    ctxt = { 
        'request' : request, 
        'due_memberships' : memberships,
        'year' : year,
        'month' : month,
        }
    return render_to_response(template, ctxt)
    
@user_passes_test(
    lambda u: u.has_perm('u.is_superuser'),
    login_url = '/halt/')
def mushroom_admin(request):
    """ Pulls up an custom admin page for the site."""
    membership_search = MembershipSearch()

    template = 'mushroom_admin.html'
    ctxt = { 
        'request' : request, 
        'membership_search' : membership_search,
        }
    return render_to_response(template, ctxt)

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
                users = User.objects.all()
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
        
