from django.contrib import admin
from .models import Speaker, Session, Attendance


@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'organization', 'title', 'email')
    search_fields = ('first_name', 'last_name', 'email', 'organization')


class SessionSpeakerInline(admin.TabularInline):
    model = Session.speakers.through
    extra = 1


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'conference', 'track', 'session_type', 'start_time', 'end_time', 'room', 'is_published')
    list_filter = ('conference', 'session_type', 'is_published', 'track')
    search_fields = ('title', 'description')
    filter_horizontal = ('speakers',)


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'session', 'joined_at')
    list_filter = ('session__conference',)
