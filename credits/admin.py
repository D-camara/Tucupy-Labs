from django.contrib import admin
from django.utils.html import format_html

from .models import CarbonCredit, CreditListing


@admin.register(CarbonCredit)
class CarbonCreditAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "owner",
        "amount",
        "unit",
        "status",
        "validation_badge",
        "validated_by",
        "generation_date",
        "created_at"
    )
    list_filter = ("status", "validation_status", "is_verified")
    search_fields = ("owner__username", "origin")
    readonly_fields = ("validated_by", "validated_at", "created_at")
    
    fieldsets = (
        ("Informações Básicas", {
            "fields": ("owner", "amount", "unit", "origin", "generation_date")
        }),
        ("Status", {
            "fields": ("status", "validation_status")
        }),
        ("Validação", {
            "fields": ("validated_by", "validated_at", "auditor_notes"),
            "classes": ("collapse",)
        }),
        ("Controle", {
            "fields": ("is_verified", "is_deleted"),
            "classes": ("collapse",)
        }),
    )
    
    def validation_badge(self, obj):
        """Exibe badge colorido do status de validação."""
        colors = {
            "PENDING": "#fbbf24",       # amarelo
            "UNDER_REVIEW": "#3b82f6",  # azul
            "APPROVED": "#10b981",      # verde
            "REJECTED": "#ef4444",      # vermelho
        }
        color = colors.get(obj.validation_status, "#6b7280")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 4px; font-weight: 600;">{}</span>',
            color,
            obj.get_validation_status_display()
        )
    validation_badge.short_description = "Validação"


@admin.register(CreditListing)
class CreditListingAdmin(admin.ModelAdmin):
    list_display = ("id", "credit", "price_per_unit", "is_active", "listed_at")
    list_filter = ("is_active",)

