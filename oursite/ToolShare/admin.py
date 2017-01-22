from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User


# Register your models here.
from .models import Tool, Registrant, ToolCategory, ToolCondition, ToolLocation, ToolStatus, Notification, ShareZone, Shed, BorrowTool, BlackoutTool

from. forms import CustomUserChangeForm, CustomUserCreationForm


class CustomUserAdmin(UserAdmin):
    # The forms to add and change user instances

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference the removed 'username' field
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'address_line1', 'address_line2', 'telephone','sharezone')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'role',
                                       'groups', 'user_permissions', 'approval_status', 'is_deleted')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'telephone')}
        ),
    )
    # form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)



admin.site.register(Tool)
admin.site.register(Registrant)
admin.site.register(ToolCategory)
admin.site.register(ToolCondition)
admin.site.register(ToolLocation)
admin.site.register(ToolStatus)
admin.site.register(Notification)
admin.site.register(ShareZone)
admin.site.register(Shed)
admin.site.register(BorrowTool)
#admin.site.register(ShedCoordinator)
admin.site.unregister(Registrant)
admin.site.register(Registrant, CustomUserAdmin)
admin.site.register(BlackoutTool)
