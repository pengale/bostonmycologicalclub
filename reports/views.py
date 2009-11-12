# Reports for the BMC project

from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.contrib.auth.decorators import (login_required, 
                                            user_passes_test, 
                                            permission_required)

from settings import MEDIA_URL
from bmc.main.models import Membership, UserProfile

@user_passes_test(
    lambda u: u.has_perm('u.is_superuser'),
    login_url = '/halt/')
def mailing_labels(request):
    """ Outputs mailing labels

    """

    memberships = Membership.objects.all()

    mem_blob = []

    for membership in memberships:
        active = False
        info = {}
        profiles = UserProfile.objects.filter(membership=membership.id)
        for profile in profiles:
            try:
                if profile.user.is_active: 
                    active = True
                    break
            except ObjectDoesNotExist:
                break

        if active:
            info['profiles'] = profiles
            info['membership'] = membership
            mem_blob.append(info)
        
    template = 'mailing_labels.csv'
    ctxt = { 
        'request' : request,
        'memberships' : memberships,
        'mem_blob': mem_blob,
        'media_url' : MEDIA_URL,        
        }
    return render_to_response(template, ctxt, mimetype='text/csv')

def memberships(request):
    """
    """

    memberships = Membership.objects.all()

    template = 'report_memberships.html'
    ctxt = {
        'memberships': memberships,
        'request': request,
        }
    return render_to_response(template, ctxt)
