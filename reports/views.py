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
from bmc.main.models import Membership, UserProfile, Due

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


def due_report(request, page=1, template_name="reports_dues.html"):
    """ Get a report of dues, ordered by most recent first
    """

    dues = Due.objects.all().order_by("-payment_date")

    return list_detail.object_list(
        request,
        template_name=template_name,
        queryset=dues,
        template_object_name='due',
        paginate_by=100,
        page=page,
        extra_context={
            'request': request,
            'media_url': MEDIA_URL, 
            }
        )
    
    

def membership_report(request, filter_by='active', page=1, format='html', 
                      template_name="reports_memberships.html", 
                      order_by='-join_date'):
    """ List of memberships
    """

    if format=='csv':
        template_name = "reports_memberships.csv"

    memberships = Membership.objects.all()

    filter_list = filter_by.split('+')

    # Fetch active, suspended, or all memberships
    if 'inactive' in filter_list:
        memberships = memberships.exclude(
            userprofile__user__is_active=True,
            )

    elif 'all' in filter_list:
        pass

    else:
        memberships = memberships.filter(
            userprofile__user__is_active=True,
            )

    if 'due' in filter_list:
        year = date.today().year
        due_by = date(int(year), 1, 1)

        memberships = memberships.exclude(
            due__paid_thru__gte=due_by,
            ).exclude(
                membership_type='Honorary',
                ).exclude(
                    membership_type='Corresponding'
                    )

    if 'corresponding' in filter_list:
        memberships = memberships.filter(
            membership_type='Corresponding',
            )

    if 'honorary' in filter_list:
        memberships = memberships.filter(
            membership_type='Honorary',
            )

    if 'noemail' in filter_list:
        memberships = memberships.filter(
            userprofile__user__email="NoEmail@BostonMycologicalClub.org",
            )
        
    memberships = memberships.order_by('-join_date').distinct()

    if format=='csv':
        template_name = 'reports_memberships.csv'
        return render_to_response(
            template_name, 
            { 'membership_list': memberships,}, 
            mimetype="text/csv"
            )

    return list_detail.object_list(
        request,
        template_name=template_name,
        queryset=memberships,
        template_object_name='membership',
        paginate_by=100,
        page = page,
        extra_context={ 
            'request': request,
            'media_url': MEDIA_URL, 
            'filter_by': filter_by,
            'order_by': order_by,
            }
        )


