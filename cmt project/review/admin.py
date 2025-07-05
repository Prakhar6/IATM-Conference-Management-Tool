from django.contrib import admin
from django.utils.html import format_html
from .models import Review
from submissions.models import Submissions
from membership.models import Membership


# Register your models here.
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('submission_title', 'conference_name', 'recommendation', 'date_reviewed', 'reviewer_name')
    list_filter = ('recommendation', 'date_reviewed', 'submission__membership__conference')
    search_fields = ('membership__user__username', 'submission__paper_title')
    readonly_fields = ('date_reviewed',)
    actions = ['mark_as_accepted', 'mark_as_rejected', 'mark_as_revision_needed']
    
    fieldsets = (
        ('Review Details', {
            'fields': ('submission', 'recommendation', 'comment')
        }),
        ('Review Information', {
            'fields': ('membership', 'date_reviewed'),
            'classes': ('collapse',)
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:  # If creating new review
            # Get or create membership for the admin user
            try:
                membership = Membership.objects.get(
                    user=request.user,
                    conference=form.base_fields['submission'].queryset.first().membership.conference
                )
            except (Membership.DoesNotExist, AttributeError):
                form.base_fields['membership'].initial = None
            else:
                form.base_fields['membership'].initial = membership
        return form

    def submission_title(self, obj):
        return format_html('<a href="/admin/submissions/submissions/{}/change/">{}</a>',
                         obj.submission.id, obj.submission.paper_title)
    submission_title.short_description = 'Submission'

    def conference_name(self, obj):
        return obj.submission.membership.conference.conference_name
    conference_name.short_description = 'Conference'

    def reviewer_name(self, obj):
        return obj.membership.user.get_full_name() or obj.membership.user.username
    reviewer_name.short_description = 'Reviewer'

    def mark_as_accepted(self, request, queryset):
        queryset.update(recommendation='ACCEPT')
    mark_as_accepted.short_description = "Mark selected reviews as Accept"
    
    def mark_as_rejected(self, request, queryset):
        queryset.update(recommendation='REJECT')
    mark_as_rejected.short_description = "Mark selected reviews as Reject"
    
    def mark_as_revision_needed(self, request, queryset):
        queryset.update(recommendation='REVISE')
    mark_as_revision_needed.short_description = "Mark selected reviews as Needs Revision"
    