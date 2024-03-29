from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from accounts.models import UserProfile


class ProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'


class ProfileAdmin(UserAdmin):
    inlines = [ ProfileInline, ]


admin.site.unregister(User)
admin.site.register(User, ProfileAdmin)
