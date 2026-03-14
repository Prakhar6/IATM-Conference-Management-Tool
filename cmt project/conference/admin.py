from django.contrib import admin
from .models import Conference, Track, Payment, RegistrationTier


class TrackInline(admin.TabularInline):
    model = Track
    extra = 1
    min_num = 1
    can_delete = True


class RegistrationTierInline(admin.TabularInline):
    model = RegistrationTier
    extra = 1
    can_delete = True


@admin.register(Conference)
class ConferenceAdmin(admin.ModelAdmin):
    list_display = ('conference_name', 'start_date', 'end_date', 'location', 'early_bird_deadline', 'submission_deadline', 'blind_review')
    list_filter = ('start_date', 'end_date', 'created_at')
    search_fields = ('conference_name', 'location')
    prepopulated_fields = {'slug': ('conference_name',)}
    ordering = ('-start_date',)
    inlines = [TrackInline, RegistrationTierInline]


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ('name', 'conference')
    list_filter = ('conference',)
    search_fields = ('name', 'conference__conference_name')
    ordering = ('conference', 'name')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'conference', 'tier', 'amount', 'status', 'created_at')
    list_filter = ('status', 'conference', 'created_at')
    search_fields = ('user__email', 'paypal_order_id')
    readonly_fields = ('paypal_order_id', 'paypal_payment_id', 'created_at', 'updated_at')


@admin.register(RegistrationTier)
class RegistrationTierAdmin(admin.ModelAdmin):
    list_display = ('name', 'conference', 'price', 'early_bird_price', 'is_active')
    list_filter = ('conference', 'is_active')
