from django.urls import path
from . import views

urlpatterns = [
    path('<slug:slug>/networking/', views.networking_hub, name='networking_hub'),
    path('<slug:slug>/group-register/', views.group_registration, name='group_registration'),
    path('<slug:slug>/analytics/', views.admin_analytics_view, name='admin_analytics'),
    path('<slug:slug>/export/attendees/', views.export_attendees_csv, name='export_attendees'),
    path('<slug:slug>/export/financials/', views.export_financials_csv, name='export_financials'),
    path('badge/<int:membership_id>/', views.download_badge, name='download_badge'),
    path('qr-ticket/<int:membership_id>/', views.download_qr_ticket, name='download_qr_ticket'),
    path('<slug:slug>/bulk-email/', views.bulk_email_view, name='bulk_email'),
]
