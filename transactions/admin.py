from django.contrib import admin

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "buyer", "seller", "credit", "amount", "total_price", "status", "timestamp")
    list_filter = ("status",)
    search_fields = ("buyer__username", "seller__username")

