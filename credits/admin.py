from django.contrib import admin

from .models import CarbonCredit, CreditListing


@admin.register(CarbonCredit)
class CarbonCreditAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "amount", "unit", "status", "generation_date", "created_at")
    list_filter = ("status",)
    search_fields = ("owner__username", "origin")


@admin.register(CreditListing)
class CreditListingAdmin(admin.ModelAdmin):
    list_display = ("id", "credit", "price_per_unit", "is_active", "listed_at")
    list_filter = ("is_active",)

