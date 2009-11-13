# Reports for the BMC project

from datetime import date

from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import list_detail
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

def membership_report(request, filter_by='active', page=1):
    """
    """
    
    memberships = Membership.objects.all()

    filter_list = filter_by.split('+')

    if 'inactive' in filter_list:
        memberships = memberships.exclude(
            userprofile__user__is_active=True,
            )
    else:
        memberships = memberships.filter(
            userprofile__user__is_active=True,
            ).distinct()

    if 'due' in filter_list:
        year = date.today().year
        due_by = date(int(year), 1, 1)

        memberships = memberships.exclude(
            due__paid_thru__gte=due_by,
            ).exclude(
                membership_type="honorary",
                ).exclude(
                    membership_type__startswith='corresponding'
                    )


    return list_detail.object_list(
        request,
        template_name='reports_memberships.html',
        queryset=memberships,
        template_object_name='membership',
        paginate_by=100,
        page = page,
        extra_context={ 
            'media_url': MEDIA_URL, 
            'filter_by': filter_by,
            }
        )


