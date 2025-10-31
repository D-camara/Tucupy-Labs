from django.contrib import admin
from django.utils.html import format_html

from .models import AuditorApplication, Profile, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "role", "is_active", "is_staff", "created_at")
    list_filter = ("role", "is_active", "is_staff")
    search_fields = ("username", "email")


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "company_name", "farm_name", "location")
    search_fields = ("user__username", "company_name", "farm_name", "location")


@admin.register(AuditorApplication)
class AuditorApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "status_badge",
        "created_at",
        "reviewed_at",
        "reviewed_by"
    )
    list_filter = ("status", "created_at", "reviewed_at")
    search_fields = ("user__username", "user__email", "justification")
    readonly_fields = ("created_at", "reviewed_at", "reviewed_by")
    
    fieldsets = (
        ("Candidato", {
            "fields": ("user", "justification")
        }),
        ("Status", {
            "fields": ("status", "rejection_reason")
        }),
        ("Revisão", {
            "fields": ("reviewed_at", "reviewed_by"),
            "classes": ("collapse",)
        }),
    )
    
    def status_badge(self, obj):
        """Exibe badge colorido do status."""
        colors = {
            "PENDING": "#fbbf24",    # amarelo
            "APPROVED": "#10b981",   # verde
            "REJECTED": "#ef4444",   # vermelho
        }
        color = colors.get(obj.status, "#6b7280")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 4px; font-weight: 600;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = "Status"
    
    actions = ["approve_applications", "reject_applications"]
    
    def approve_applications(self, request, queryset):
        """Action para aprovar candidaturas selecionadas."""
        from accounts.emails import send_auditor_approval_notification
        
        count = 0
        for application in queryset.filter(status=AuditorApplication.Status.PENDING):
            application.approve(request.user)
            
            # Envia email de aprovação
            try:
                send_auditor_approval_notification(
                    user_email=application.user.email,
                    user_name=application.user.get_full_name() or application.user.username
                )
            except Exception as e:
                self.message_user(
                    request,
                    f"Erro ao enviar email para {application.user.username}: {str(e)}",
                    level="warning"
                )
            
            count += 1
        
        self.message_user(
            request,
            f"{count} candidatura(s) aprovada(s) com sucesso!",
            level="success"
        )
    approve_applications.short_description = "✅ Aprovar candidaturas selecionadas"
    
    def reject_applications(self, request, queryset):
        """Action para rejeitar candidaturas selecionadas."""
        from accounts.emails import send_auditor_rejection_notification
        
        count = 0
        for application in queryset.filter(status=AuditorApplication.Status.PENDING):
            reason = "Sua candidatura não foi aprovada neste momento."
            application.reject(request.user, reason)
            
            # Envia email de rejeição
            try:
                send_auditor_rejection_notification(
                    user_email=application.user.email,
                    user_name=application.user.get_full_name() or application.user.username,
                    reason=reason
                )
            except Exception as e:
                self.message_user(
                    request,
                    f"Erro ao enviar email para {application.user.username}: {str(e)}",
                    level="warning"
                )
            
            count += 1
        
        self.message_user(
            request,
            f"{count} candidatura(s) rejeitada(s).",
            level="success"
        )
    reject_applications.short_description = "❌ Rejeitar candidaturas selecionadas"

