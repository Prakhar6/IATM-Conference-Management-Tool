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
    list_filter = ('start_date', 'end_date', 'created_at')
    search_fields = ('conference_name', 'location')
    prepopulated_fields = {'slug': ('conference_name',)}
    ordering = ('-start_date',)
    inlines = [TrackInline]

@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ('name', 'conference')
    list_filter = ('conference',)
    search_fields = ('name', 'conference__conference_name')
    ordering = ('conference', 'name')
