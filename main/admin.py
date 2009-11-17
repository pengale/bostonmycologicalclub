""" Specifies which objects in models.py appear in the Admin
interface.  """

from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin
from bmc.main.models import (Membership, UserProfile, WalkArea, Walk, 
                             Announcement, Newsbit, IDSession, Page, Due)
from django.utils.translation import ugettext, ugettext_lazy as _

admin.site.unregister(User)
admin.site.unregister(Group)

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    extra = 1

    fields = ('membership', 'user', 'title', 'phone', 'alt_phone', 'notes', )

class DueInline(admin.TabularInline):
    model = Due
    extra = 1

class MemberAdmin(UserAdmin):

    inlines = [UserProfileInline]
    list_display = ('username', 'first_name', 'last_name', 'email', 'is_active')
    actions = ['toggle_active']

    fieldsets = (
        (None, {
                'fields': ('username', 'password'),
                }),
        (_('Personal info'), {
                'fields': ('first_name', 'last_name', 'email'),
                }),
        (_('Permissions'), {
                'classes': ('collapse',),
                'fields': ('is_staff', 'is_active', 'is_superuser', 'user_permissions'),
                }),
        (_('Important dates'), {
                'classes': ('collapse',),
                'fields': ('last_login', 'date_joined'),
                }),
        #(_('Groups'), {
        #        'classes': ('collapse',)
        #        'fields': ('groups',)
        #        }),
    )

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

    list_display = ('__unicode__', 'id', 'join_date', 
                    'membership_type','is_active',)
    list_filter = ('membership_type',)
    search_fields = [
        'address', 
        'userprofile__user__first_name',
        'userprofile__user__last_name',
        ]
    actions = ['toggle_suspend']
    
    def toggle_suspend(self, request, queryset):
        for entry in queryset:
            profiles = UserProfile.objects.filter(membership=entry.id)
            if entry.is_active:
                for profile in profiles:
                    profile.user.is_active = False
                    profile.user.save()
            else:
                for profile in profiles:
                    profile.user.is_active = True
                    profiles.user.save()
                
            


admin.site.register(Membership, MembershipAdmin)

class DueAdmin(admin.ModelAdmin):
    list_display = ('payment_amount', 'membership', 'payment_date', 
                    'payment_type', 'paid_thru', 'notes')
admin.site.register(Due, DueAdmin)


#admin.site.register(Membership)
#admin.site.register(UserProfile)
admin.site.register(WalkArea)
admin.site.register(Walk)
admin.site.register(Announcement)
admin.site.register(Newsbit)
admin.site.register(IDSession)
#admin.site.register(Page)




