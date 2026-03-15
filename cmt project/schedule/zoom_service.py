"""
Zoom API integration for auto-creating meetings/webinars for conference sessions.

Uses Zoom Server-to-Server OAuth (recommended for backend apps).
Requires ZOOM_ACCOUNT_ID, ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET in settings/env.
"""
import requests
import logging
from datetime import datetime
from django.conf import settings

logger = logging.getLogger(__name__)

ZOOM_TOKEN_URL = 'https://zoom.us/oauth/token'
ZOOM_API_BASE = 'https://api.zoom.us/v2'


def _get_access_token():
    """Get OAuth access token using Server-to-Server OAuth credentials."""
    account_id = getattr(settings, 'ZOOM_ACCOUNT_ID', '')
    client_id = getattr(settings, 'ZOOM_CLIENT_ID', '')
    client_secret = getattr(settings, 'ZOOM_CLIENT_SECRET', '')

    if not all([account_id, client_id, client_secret]):
        raise ValueError("Zoom API credentials not configured. Set ZOOM_ACCOUNT_ID, ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET.")

    response = requests.post(
        ZOOM_TOKEN_URL,
        params={'grant_type': 'account_credentials', 'account_id': account_id},
        auth=(client_id, client_secret),
        timeout=10,
    )
    response.raise_for_status()
    return response.json()['access_token']


def create_zoom_meeting(session):
    """
    Create a Zoom meeting for a Session instance.
    Returns dict with meeting_id, join_url, and passcode.
    """
    token = _get_access_token()
    user_id = getattr(settings, 'ZOOM_USER_ID', 'me')

    # Format start time for Zoom (ISO 8601)
    start_time = session.start_time.strftime('%Y-%m-%dT%H:%M:%S')
    duration = session.duration_minutes

    payload = {
        'topic': session.title,
        'type': 2,  # Scheduled meeting
        'start_time': start_time,
        'duration': duration,
        'timezone': settings.TIME_ZONE,
        'agenda': session.description[:2000] if session.description else '',
        'settings': {
            'join_before_host': True,
            'mute_upon_entry': True,
            'waiting_room': False,
            'auto_recording': 'cloud',
            'meeting_authentication': False,
        },
    }

    response = requests.post(
        f'{ZOOM_API_BASE}/users/{user_id}/meetings',
        json=payload,
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()

    return {
        'meeting_id': str(data['id']),
        'join_url': data['join_url'],
        'passcode': data.get('password', ''),
    }


def delete_zoom_meeting(meeting_id):
    """Delete a Zoom meeting by its ID."""
    if not meeting_id:
        return

    try:
        token = _get_access_token()
        response = requests.delete(
            f'{ZOOM_API_BASE}/meetings/{meeting_id}',
            headers={'Authorization': f'Bearer {token}'},
            timeout=10,
        )
        response.raise_for_status()
    except Exception as e:
        logger.warning(f"Failed to delete Zoom meeting {meeting_id}: {e}")


def update_zoom_meeting(meeting_id, session):
    """Update an existing Zoom meeting when session details change."""
    if not meeting_id:
        return

    try:
        token = _get_access_token()
        start_time = session.start_time.strftime('%Y-%m-%dT%H:%M:%S')

        payload = {
            'topic': session.title,
            'start_time': start_time,
            'duration': session.duration_minutes,
            'agenda': session.description[:2000] if session.description else '',
        }

        response = requests.patch(
            f'{ZOOM_API_BASE}/meetings/{meeting_id}',
            json=payload,
            headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
            timeout=15,
        )
        response.raise_for_status()
    except Exception as e:
        logger.warning(f"Failed to update Zoom meeting {meeting_id}: {e}")
