from django.conf.urls.defaults import *
from django.contrib import admin
from bmc.main.views import *
from django.contrib.auth.views import *

admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', index),

    # Walks
    (r'^walks/list/(start(?P<start>[0-9]+)/)?((?P<per_page>[0-9]+)pp/)?', list_walks),
    (r'^walks/create/', create_walk),
    (r'^walks/edit/((?P<walk>[0-9]+)/)?', edit_walk),
    (r'^walks/view/((?P<walk>[0-9]+)/)?', view_walk),
    (r'^walks/mushrooms/((?P<walk>[0-9]+)/)?', mushrooms),

    #Membership Tools
    (r'^memberships/list/(start(?P<start>[0-9]+)/)?((?P<per_page>[0-9]+)pp/)?((?P<due_by>due_by)/((?P<year>[1-2][0-9][0-9][0-9])/(?P<month>([0-1])?[0-9])/)?)?', list_memberships),
    (r'^memberships/((?P<membership>[0-9]+)/)?view/', view_membership),
    (r'^memberships/((?P<membership>[0-9]+)/)?edit/', edit_membership ),
    (r'^memberships/create/', create_membership ),
    (r'^memberships/((?P<membership>[0-9]+)/)?edit_user/((?P<user>[0-9]+)/)?', edit_user),
    (r'^memberships/(?P<membership>[0-9]+)/status/(?P<action>suspend|restore)/', membership_status),
    (r'^memberships/((?P<membership>[0-9]+)/)?edit_due/((?P<due>[0-9]+)/)?', edit_due),
    (r'^memberships/((?P<membership>[0-9]+)/)?dues/', view_dues),
    (r'^memberships/search/', membership_search),
    (r'^memberships/fetch/', membership_fetch),

    # 'Static' Pages
    (r'^schedule', schedule),
    (r'^ClubActivities\.html$', schedule),  # legacy compatibility
    (r'^about', about),
    (r'^membership.html$', about),  # legacy compatibility
    (r'^application', application),
    (r'^application.html$', application),  # legacy compatibility
    (r'^[Ss]tories/(?P<year>2[0-9][0-9][0-9])/(?P<month>[0-1][0-9])/(?P<day>[0-3][0-9])/(?P<time>[0-2][0-9]:[0-5][0-9]:[0-5][0-9])/$', story),
    (r'^(.*)\.html$', page),
    (r'^([a-z0-9\-]+)\.css$', style),

    # Admin Stuff
    (r'^mushroom_admin/(?P<entries>[a-z]+)/((?P<entry_id>[0-9]+)/)?(edit|create)/', mushroom_admin_edit),
    (r'^mushroom_admin/(?P<entries>[a-z]+)/(?P<entry_id>[0-9]+)/', mushroom_admin_view),
    (r'^mushroom_admin/(?P<entries>[a-z]+)/(start(?P<start>[0-9]+)/)?((?P<per_page>[0-9]+)pp/)?', mushroom_admin_list),
    (r'^mushroom_admin', mushroom_admin),

    (r'^email/list/', list_emails),
    (r'^email/send/', send_email),
    (r'^email/sent/', sent_email),
    (r'^admin/(.*)', admin.site.root),

    # Finger wagging 'you don't have permission' page
    (r'^halt', halt),

    # User tools
    (r'^accounts/profile/edit/', edit_profile),
    (r'^accounts/profile/$', profile),
)

urlpatterns += patterns('django.contrib.auth.views',
    (r'^accounts/login/$', 'login', { 'template_name' : 'login.html' }),
    (r'^accounts/logout/$', 'logout_then_login'),
    (r'^accounts/password_change/$', 'password_change'),
    (r'^accounts/password_change_done/$', 'password_change_done'),
#    (r'^accounts/password_reset/$', 'password_reset'),
    (r'^accounts/password_reset/$', 'password_reset', { 'template_name' : 'registration/password_reset_form.html' }),
    (r'^accounts/password_reset/done/$', 'password_reset_done'),
    (r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'password_reset_confirm'),
    (r'^reset/done/$', 'password_reset_complete'),
)

urlpatterns += patterns('',
    (r'^.*', error_404),  # nice 404 page
)

