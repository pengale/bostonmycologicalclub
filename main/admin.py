""" Specifies which objects in models.py appear in the Admin
interface.  """

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from bmc.main.models import (Membership, UserProfile, WalkArea, Walk, 
                             Announcement, Newsbit, IDSession, Page, Due)

""" Long way to do things, for reference: """
#class UserProfileAdmin(admin.ModelAdmin):
#    pass
#admin.site.register(UserProfile, UserProfileAdmin)

admin.site.unregister(User)

class UserProfileInline(admin.TabularInline):
    model = UserProfile
    extra = 1

    fields = ('user', 'title', 'phone', 'alt_phone', 'notes',)

class DueInline(admin.TabularInline):
    model = Due
    extra = 1

class MemberAdmin(UserAdmin):

    inlines = [UserProfileInline, DueInline]
    list_display = ('username', 'first_name', 'last_name', 'email')
    actions = ['toggle_active']

    def toggle_active(self, request, queryset):
        for entry in queryset:
            if entry.active == False:
                entry.active=True
                entry.save()
            else:
                entry.active = False
                entry.save()
    toggle_active.short_description = "Toggle 'active' status"

admin.site.register(User, MemberAdmin)


class MembershipAdmin(admin.ModelAdmin):

    inlines = [
        UserProfileInline,
        DueInline,
        ]

    list_display = ('id', 'address', 'address2', 'get_name_list', 'join_date', 'membership_type',)
    list_filter = ('membership_type',)
    search_fields = ['address']
admin.site.register(Membership, MembershipAdmin)

class DueAdmin(admin.ModelAdmin):
    list_display = ('payment_amount', 'membership', 'payment_date', 
                    'payment_type', 'paid_thru', 'notes')
admin.site.register(Due, DueAdmin)


#admin.site.register(Membership)
admin.site.register(UserProfile)
admin.site.register(WalkArea)
admin.site.register(Walk)
admin.site.register(Announcement)
admin.site.register(Newsbit)
admin.site.register(IDSession)
admin.site.register(Page)




