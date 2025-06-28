from django.contrib import admin
from .models import Membership

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'conference', 'role1', 'role2', 'status', 'is_paid', 'created_at')
    list_filter = ('status', 'role1', 'role2', 'is_paid')
    search_fields = ('user__username', 'conference__conference_name')
    readonly_fields = ('created_at',)

    fieldsets = (
        (None, {
            'fields': ('user', 'conference', 'role1', 'role2', 'status', 'is_paid')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )
