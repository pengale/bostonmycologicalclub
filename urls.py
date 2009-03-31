from django.conf.urls.defaults import *
from django.contrib import admin
from bmc.main.views import *
from django.contrib.auth.views import *

admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', index),

    # Walks
    (r'^walks/(?P<action>list|create|done|edit|view|mushrooms)(/(?P<walk>[0-9]+))?', walks),

    # Static Pages
    (r'^ClubActivities\.html$', schedule),  # legacy compatibility
    (r'^schedule/$',schedule),
    (r'^[Ss]tories/(?P<year>2[0-9][0-9][0-9])/(?P<month>[0-1][0-9])/(?P<day>[0-3][0-9])/(?P<time>[0-2][0-9]:[0-5][0-9]:[0-5][0-9])/$', story),
    (r'^(.*)\.html$', page),
    (r'^([a-z0-9\-]+)\.css$', style),

    # Admin Stuff
    (r'^mushroom_admin', mushroom_admin),
    (r'^members/list/due/(?P<year>[0-9][0-9][0-9][0-9])/(?P<month>)[0-9][0-9]/', memberships_due),
    (r'^members/((?P<membership>[0-9]+)/)?(?P<action>list|done|edit|view|edit_user|edit_due|status|dues|search)/(?P<criteria>[0-9a-z]+)?', memberships),
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

