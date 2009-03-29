""" Specifies which objects in models.py appear in the Admin
interface.  """

from django.contrib import admin
from bmc.main.models import Membership, UserProfile, WalkArea, Walk, Announcement, Newsbit, PublicWalk, IDSession, Page

""" Long way to do things, for reference: """
#class UserProfileAdmin(admin.ModelAdmin):
#    pass
#admin.site.register(UserProfile, UserProfileAdmin)

admin.site.register(Membership)
admin.site.register(UserProfile)
admin.site.register(WalkArea)
admin.site.register(Walk)
admin.site.register(Announcement)
admin.site.register(Newsbit)
admin.site.register(PublicWalk)
admin.site.register(IDSession)
admin.site.register(Page)




