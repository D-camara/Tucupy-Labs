from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Profile


class RegistrationForm(UserCreationForm):
    """Formulário de registro de novos usuários (com escolha de papel)."""
    role = forms.ChoiceField(
        choices=User.Roles.choices,
        label="Tipo de conta",
        initial=User.Roles.COMPANY,
        widget=forms.Select(attrs={"class": "form-select"})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "role")
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-input"}),
            "email": forms.EmailInput(attrs={"class": "form-input"}),
        }

    def save(self, commit: bool = True) -> User:
        """Salva o usuário e define o papel corretamente."""
        user = super().save(commit=False)
        user.email = self.cleaned_data.get("email", "")
        user.role = self.cleaned_data.get("role", User.Roles.COMPANY)
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    """Formulário para edição do perfil do usuário."""
    class Meta:
        model = Profile
        fields = ["company_name", "farm_name", "location", "tax_id", "phone"]
        widgets = {
            "company_name": forms.TextInput(attrs={"class": "form-input"}),
            "farm_name": forms.TextInput(attrs={"class": "form-input"}),
            "location": forms.TextInput(attrs={"class": "form-input"}),
            "tax_id": forms.TextInput(attrs={"class": "form-input"}),
            "phone": forms.TextInput(attrs={"class": "form-input"}),
        }
