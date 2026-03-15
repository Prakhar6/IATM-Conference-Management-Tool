from django.urls import path
from . import views

urlpatterns = [
    path('<slug:slug>/networking/', views.networking_hub, name='networking_hub'),
    path('<slug:slug>/group-register/', views.group_registration, name='group_registration'),
    path('<slug:slug>/group-register/success/', views.group_payment_success, name='group_payment_success'),
    path('<slug:slug>/analytics/', views.admin_analytics_view, name='admin_analytics'),
    path('<slug:slug>/export/attendees/', views.export_attendees_csv, name='export_attendees'),
    path('<slug:slug>/export/financials/', views.export_financials_csv, name='export_financials'),
    path('badge/<int:membership_id>/', views.download_badge, name='download_badge'),
    path('qr-ticket/<int:membership_id>/', views.download_qr_ticket, name='download_qr_ticket'),
    path('<slug:slug>/bulk-email/', views.bulk_email_view, name='bulk_email'),
    path('messages/', views.message_inbox, name='message_inbox'),
    path('messages/<int:message_id>/', views.message_detail, name='message_detail'),
    path('<slug:slug>/message/<int:recipient_id>/', views.send_message, name='send_message'),
]
