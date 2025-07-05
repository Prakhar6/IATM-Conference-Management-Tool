from django.contrib import admin
from .models import Submissions


# Register your models here.
@admin.register(Submissions)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('paper_title', 'membership', 'submission_date', 'status')
    list_filter = ('status', 'submission_date')
    search_fields = ('paper_title', 'membership__user__email', 'membership__user__first_name', 'membership__user__last_name')
    readonly_fields = ('submission_date',)
    actions = ['mark_as_accepted', 'mark_as_rejected']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('membership__user')
    
    def mark_as_accepted(self, request, queryset):
        queryset.update(status='ACCEPTED')
    mark_as_accepted.short_description = "Mark selected submissions as accepted"
    
    def mark_as_rejected(self, request, queryset):
        queryset.update(status='REJECTED')
    mark_as_rejected.short_description = "Mark selected submissions as rejected"