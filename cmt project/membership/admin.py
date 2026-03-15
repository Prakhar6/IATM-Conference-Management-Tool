from django.contrib import admin
from .models import Membership, AttendeeMessage

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'conference', 'role1', 'role2', 'is_paid', 'messaging_opt_in', 'created_at')
    list_filter = ('role1', 'role2', 'is_paid', 'messaging_opt_in')
    search_fields = ('user__email', 'conference__conference_name')
    readonly_fields = ('created_at',)

    fieldsets = (
        (None, {
            'fields': ('user', 'conference', 'role1', 'role2', 'is_paid', 'messaging_opt_in')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )


@admin.register(AttendeeMessage)
class AttendeeMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'conference', 'subject', 'is_read', 'created_at')
    list_filter = ('conference', 'is_read')
    search_fields = ('sender__email', 'recipient__email', 'subject')
    readonly_fields = ('created_at',)
