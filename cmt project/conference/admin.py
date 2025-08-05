from django.contrib import admin
from .models import Conference, Track

class TrackInline(admin.TabularInline):
    model = Track
    extra = 1  # How many empty forms to show by default
    min_num = 1
    can_delete = True

@admin.register(Conference)
class ConferenceAdmin(admin.ModelAdmin):
    list_display = ('conference_name', 'start_date', 'end_date', 'location', 'created_at')
    list_filter = ('start_date', 'location')
    search_fields = ('conference_name', 'conference_description', 'location')
    ordering = ('-start_date',)
    prepopulated_fields = {'slug': ('conference_name',)}

    fieldsets = (
        (None, {
            'fields': ('conference_name', 'conference_description', 'slug')
        }),
        ('Dates & Location', {
            'fields': ('start_date', 'end_date', 'location')
        }),
        ('Meta', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('created_at',)

    inlines = [TrackInline]
