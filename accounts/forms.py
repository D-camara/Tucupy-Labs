from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Profile


class RegistrationForm(UserCreationForm):
    """Formulário de registro de novos usuários (com escolha de papel).
    
    Nota: A opção ADMIN não está disponível no registro público.
    Administradores devem ser criados via Django admin por um superuser.
    """
    
    # Sobrescrever campos para adicionar classes CSS
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent",
            "placeholder": "seu_usuario"
        })
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent",
            "placeholder": "seu@email.com"
        })
    )
    
    password1 = forms.CharField(
        label="Senha",
        strip=False,
        widget=forms.PasswordInput(attrs={
            "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent",
            "placeholder": "••••••••"
        })
    )
    
    password2 = forms.CharField(
        label="Confirmar senha",
        strip=False,
        widget=forms.PasswordInput(attrs={
            "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent",
            "placeholder": "••••••••"
        })
    )
    
    # Apenas PRODUCER e COMPANY disponíveis para registro público
    role = forms.ChoiceField(
        choices=[
            (User.Roles.PRODUCER, 'Produtor'),
            (User.Roles.COMPANY, 'Empresa'),
        ],
        label="Tipo de conta",
        initial=User.Roles.COMPANY,
        widget=forms.RadioSelect()
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "role")

    def save(self, commit: bool = True) -> User:
        """Salva o usuário e define o papel corretamente."""
        user = super().save(commit=False)
        user.email = self.cleaned_data.get("email", "")
        user.role = self.cleaned_data.get("role", User.Roles.COMPANY)
        if commit:
            user.save()
        return user


class CustomLoginForm(AuthenticationForm):
    """Formulário de login customizado com estilos Tucupi Labs."""
    
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:border-tucupi-green-500 focus:ring-2 focus:ring-tucupi-green-500/50 focus:outline-none transition",
            "placeholder": "seu_usuario",
            "autocomplete": "username"
        })
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:border-tucupi-green-500 focus:ring-2 focus:ring-tucupi-green-500/50 focus:outline-none transition",
            "placeholder": "••••••••",
            "autocomplete": "current-password"
        })
    )
    
    error_messages = {
        'invalid_login': "Nome de usuário ou senha incorretos. Tente novamente.",
        'inactive': "Esta conta está inativa.",
    }


class ProfileForm(forms.ModelForm):
    """Formulário para edição do perfil do usuário."""
    class Meta:
        model = Profile
        fields = ["company_name", "farm_name", "location", "tax_id", "phone"]
        widgets = {
            "company_name": forms.TextInput(attrs={
                "class": "w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:border-tucupi-green-500 focus:ring-2 focus:ring-tucupi-green-500/50 focus:outline-none transition",
                "placeholder": "Nome da empresa"
            }),
            "farm_name": forms.TextInput(attrs={
                "class": "w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:border-tucupi-green-500 focus:ring-2 focus:ring-tucupi-green-500/50 focus:outline-none transition",
                "placeholder": "Nome da fazenda"
            }),
            "location": forms.TextInput(attrs={
                "class": "w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:border-tucupi-green-500 focus:ring-2 focus:ring-tucupi-green-500/50 focus:outline-none transition",
                "placeholder": "Cidade, Estado"
            }),
            "tax_id": forms.TextInput(attrs={
                "class": "w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:border-tucupi-green-500 focus:ring-2 focus:ring-tucupi-green-500/50 focus:outline-none transition",
                "placeholder": "CPF/CNPJ"
            }),
            "phone": forms.TextInput(attrs={
                "class": "w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:border-tucupi-green-500 focus:ring-2 focus:ring-tucupi-green-500/50 focus:outline-none transition",
                "placeholder": "(00) 00000-0000"
            }),
        }
