# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils import timezone

from .models import User, AuditorProfile

# ----- Actions -----
@admin.action(description="Aprovar usuários selecionados (liberar acesso)")
def approve_users(modeladmin, request, queryset):
    updated = 0
    for user in queryset:
        if not user.is_active:
            user.is_active = True
            user.approved_at = timezone.now()
            user.save(update_fields=["is_active", "approved_at"])
            updated += 1
    modeladmin.message_user(request, f"{updated} usuário(s) aprovado(s).")

@admin.action(description="Desativar usuários selecionados (remover acesso)")
def deactivate_users(modeladmin, request, queryset):
    updated = queryset.update(is_active=False)
    modeladmin.message_user(request, f"{updated} usuário(s) desativado(s).")

# ----- User Admin -----
@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """
    Admin para o User customizado (AUTH_USER_MODEL = accounts.User).
    Mantém a UI padrão do Django e adiciona campos/ações do EcoTrade.
    """

    # Colunas na listagem
    list_display = (
        "username",
        "email",
        "role",
        "is_active",
        "is_verified",
        "approved_at",
        "date_joined",
        "last_login",
    )
    list_filter = ("role", "is_active", "is_verified", "is_staff", "is_superuser")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("-date_joined",)
    # Campos somente leitura
    readonly_fields = ("last_login", "date_joined", "approved_at")

    # Fieldsets: base do Django + seção EcoTrade
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Informações pessoais", {"fields": ("first_name", "last_name", "email")}),
        (
            "Permissões",
            {
                "fields": (
                    "is_active",
                    "is_verified",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Datas importantes", {"fields": ("last_login", "date_joined", "approved_at")}),
        ("EcoTrade", {"fields": ("role",)}),
    )

    # Form de criação
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2", "role"),
            },
        ),
    )

    actions = [approve_users, deactivate_users]

# ----- Auditor Profile Admin -----
@admin.register(AuditorProfile)
class AuditorProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "organization", "document_id", "phone")
    search_fields = (
        "user__username",
        "user__email",
        "full_name",
        "organization",
        "document_id",
        "phone",
    )
    list_select_related = ("user",)




