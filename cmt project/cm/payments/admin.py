from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'conference', 'amount', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'conference']
    search_fields = ['user__email', 'conference__conference_name', 'paypal_order_id']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'conference')
        }),
        ('Payment Details', {
            'fields': ('amount', 'currency', 'status')
        }),
        ('PayPal Information', {
            'fields': ('paypal_order_id', 'paypal_payment_id')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
