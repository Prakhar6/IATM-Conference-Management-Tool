from django.contrib import admin
from django import forms
from django.contrib import messages
from .models import Speaker, Session, Attendance
import logging

logger = logging.getLogger(__name__)


@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'organization', 'title', 'email')
    search_fields = ('first_name', 'last_name', 'email', 'organization')


class SessionAdminForm(forms.ModelForm):
    auto_create_zoom = forms.BooleanField(
        required=False,
        initial=False,
        label="Auto-create Zoom meeting",
        help_text="Check this to automatically create a Zoom meeting for this session. "
                  "Requires Zoom API credentials in settings.",
    )

    class Meta:
        model = Session
        fields = '__all__'


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    form = SessionAdminForm
    list_display = ('title', 'conference', 'track', 'session_type', 'start_time', 'end_time', 'room', 'has_zoom', 'is_published')
    list_filter = ('conference', 'session_type', 'is_published', 'track')
    search_fields = ('title', 'description')
    filter_horizontal = ('speakers',)
    readonly_fields = ('zoom_meeting_id', 'zoom_meeting_url', 'zoom_passcode')

    fieldsets = (
        (None, {
            'fields': ('conference', 'track', 'title', 'description', 'session_type', 'speakers'),
        }),
        ('Schedule', {
            'fields': ('start_time', 'end_time', 'room', 'is_published'),
        }),
        ('Virtual Meeting (Zoom)', {
            'fields': ('auto_create_zoom', 'zoom_meeting_id', 'zoom_meeting_url', 'zoom_passcode'),
            'description': 'Zoom meeting details are auto-populated when "Auto-create Zoom meeting" is checked. '
                           'You can also manually enter meeting details.',
        }),
    )

    def has_zoom(self, obj):
        return bool(obj.zoom_meeting_url)
    has_zoom.boolean = True
    has_zoom.short_description = 'Zoom'

    def save_model(self, request, obj, form, change):
        auto_create = form.cleaned_data.get('auto_create_zoom', False)

        if auto_create and not obj.zoom_meeting_id:
            # Create new Zoom meeting
            try:
                from .zoom_service import create_zoom_meeting
                result = create_zoom_meeting(obj)
                obj.zoom_meeting_id = result['meeting_id']
                obj.zoom_meeting_url = result['join_url']
                obj.zoom_passcode = result['passcode']
                messages.success(request, f"Zoom meeting created: {result['meeting_id']}")
            except Exception as e:
                messages.error(request, f"Failed to create Zoom meeting: {e}")
        elif auto_create and obj.zoom_meeting_id and change:
            # Update existing Zoom meeting
            try:
                from .zoom_service import update_zoom_meeting
                update_zoom_meeting(obj.zoom_meeting_id, obj)
                messages.info(request, f"Zoom meeting {obj.zoom_meeting_id} updated.")
            except Exception as e:
                messages.warning(request, f"Failed to update Zoom meeting: {e}")

        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        if obj.zoom_meeting_id:
            try:
                from .zoom_service import delete_zoom_meeting
                delete_zoom_meeting(obj.zoom_meeting_id)
                messages.info(request, f"Zoom meeting {obj.zoom_meeting_id} deleted.")
            except Exception as e:
                messages.warning(request, f"Failed to delete Zoom meeting: {e}")
        super().delete_model(request, obj)


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'session', 'joined_at')
    list_filter = ('session__conference',)
