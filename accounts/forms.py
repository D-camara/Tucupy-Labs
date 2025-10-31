from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, AuditorProfile

class AuditorRegistrationForm(UserCreationForm):
    """
Cadastro de Auditor:
    - Cria User com role = AUDITOR e is_active = False (aguarda aprovação).
    - Cria/atualiza AuditorProfile com dados do formulário.
    """
    email = forms.EmailInput()
    full_name = forms.CharField(label="Nome completo", max_length=255)
    organization = forms.CharField(label="Organização", max_length=255, required=False)
    document_id = forms.CharField(label="Documento/Registro", max_length=100, required=False)
    phone = forms.CharField(label="Telefone", max_length=64, required=False)
    notes = forms.CharField(label="Observações", widget=forms.Textarea, required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "full_name", "organization", "document_id", "phone", "notes")

    def save(self, commit: bool = True) -> User:
        user = super().save(commit=False)
        # Força papel e trava acesso até aprovação
        user.role = User.Roles.AUDITOR
        user.email = self.cleaned_data.get("email", "")
        user.is_active = False  # sem acesso até Admin liberar
        if commit:
            user.save()

            profile_data = {
                "full_name": self.cleaned_data.get("full_name"),
                "organization": self.cleaned_data.get("organization", ""),
                "document_id": self.cleaned_data.get("document_id", ""),
                "phone": self.cleaned_data.get("phone", ""),
                "notes": self.cleaned_data.get("notes", ""),
            }
            # Garante um perfil consistente
            profile, _ = AuditorProfile.objects.get_or_create(user=user)
            for k, v in profile_data.items():
                setattr(profile, k, v)
            profile.save()

        return user

