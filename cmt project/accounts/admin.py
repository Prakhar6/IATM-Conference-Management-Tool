from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    ordering = ['email']
    list_display = ['email', 'first_name', 'last_name', 'is_staff', 'occupation']
    search_fields = ['email', 'first_name', 'last_name', 'organization']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'country', 'organization', 'phone', 'occupation', 'iatm_membership')
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'password1', 'password2',
                'first_name', 'last_name',
                'country', 'organization', 'phone', 'occupation',
                'iatm_membership',
                'is_staff', 'is_superuser', 'is_active',
                'groups', 'user_permissions'
            ),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)
