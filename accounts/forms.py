from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import AuditorApplication, AuditorProfile, User, Profile


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


class AuditorApplicationForm(forms.ModelForm):
    """Formulário de candidatura para auditor."""
    
    class Meta:
        model = AuditorApplication
        fields = [
            "full_name",
            "email",
            "phone",
            "organization",
            "linkedin_url",
            "certificate",
            "resume",
            "justification",
            "terms_accepted"
        ]
        widgets = {
            "full_name": forms.TextInput(attrs={
                "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition",
                "placeholder": "Seu nome completo"
            }),
            "email": forms.EmailInput(attrs={
                "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition",
                "placeholder": "seu@email.com"
            }),
            "phone": forms.TextInput(attrs={
                "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition",
                "placeholder": "(11) 99999-9999"
            }),
            "organization": forms.TextInput(attrs={
                "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition",
                "placeholder": "Empresa ou autônomo"
            }),
            "linkedin_url": forms.URLInput(attrs={
                "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition",
                "placeholder": "https://linkedin.com/in/seu-perfil"
            }),
            "certificate": forms.FileInput(attrs={
                "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100",
                "accept": ".pdf,.jpg,.jpeg,.png"
            }),
            "resume": forms.FileInput(attrs={
                "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100",
                "accept": ".pdf"
            }),
            "justification": forms.Textarea(attrs={
                "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition",
                "placeholder": "Explique sua experiência e por que você quer ser um auditor...",
                "rows": 5
            }),
            "terms_accepted": forms.CheckboxInput(attrs={
                "class": "w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded focus:ring-green-500 focus:ring-2"
            }),
        }
        labels = {
            "full_name": "Nome Completo *",
            "email": "Email *",
            "phone": "Telefone",
            "organization": "Organização",
            "linkedin_url": "LinkedIn",
            "certificate": "Certificado *",
            "resume": "Currículo (PDF)",
            "justification": "Motivação *",
            "terms_accepted": "Li e aceito os termos de auditoria"
        }
        help_texts = {
            "phone": "Formato: (XX) XXXXX-XXXX",
            "organization": "Empresa onde trabalha ou se é autônomo",
            "linkedin_url": "URL completa do seu perfil no LinkedIn",
            "certificate": "Upload de certificado de qualificação (PDF ou imagem)",
            "resume": "Opcional - Upload do seu currículo em PDF",
            "justification": "Por que você quer ser um auditor na EcoTrade? Explique sua experiência e qualificações.",
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Preenche automaticamente com dados do usuário se disponível
        if self.user and not self.instance.pk:
            self.fields['full_name'].initial = self.user.get_full_name() or self.user.username
            self.fields['email'].initial = self.user.email
            if hasattr(self.user, 'profile'):
                self.fields['phone'].initial = self.user.profile.phone
    
    def clean_certificate(self):
        """Valida o certificado."""
        certificate = self.cleaned_data.get('certificate')
        if certificate:
            # Verifica tamanho (máx 5MB)
            if certificate.size > 5 * 1024 * 1024:
                raise forms.ValidationError("O arquivo deve ter no máximo 5MB.")
            
            # Verifica extensão
            ext = certificate.name.split('.')[-1].lower()
            if ext not in ['pdf', 'jpg', 'jpeg', 'png']:
                raise forms.ValidationError("Apenas PDF ou imagens (JPG, PNG) são permitidos.")
        
        return certificate
    
    def clean_resume(self):
        """Valida o currículo."""
        resume = self.cleaned_data.get('resume')
        if resume:
            # Verifica tamanho (máx 5MB)
            if resume.size > 5 * 1024 * 1024:
                raise forms.ValidationError("O arquivo deve ter no máximo 5MB.")
            
            # Verifica extensão
            ext = resume.name.split('.')[-1].lower()
            if ext != 'pdf':
                raise forms.ValidationError("Apenas arquivos PDF são permitidos.")
        
        return resume
    
    def clean_terms_accepted(self):
        """Valida que os termos foram aceitos."""
        terms_accepted = self.cleaned_data.get('terms_accepted')
        if not terms_accepted:
            raise forms.ValidationError("Você deve aceitar os termos para se candidatar.")
        return terms_accepted
    
    def clean_linkedin_url(self):
        """Valida URL do LinkedIn."""
        url = self.cleaned_data.get('linkedin_url')
        if url and 'linkedin.com' not in url.lower():
            raise forms.ValidationError("Por favor, insira uma URL válida do LinkedIn.")
        return url


class AuditorRegistrationForm(UserCreationForm):
    """Formulário combinado: cria usuário E candidatura de auditor ao mesmo tempo."""
    
    # Dados do usuário
    username = forms.CharField(
        label="Nome de usuário",
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/50 focus:outline-none transition",
            "placeholder": "seu_usuario"
        })
    )
    
    password1 = forms.CharField(
        label="Senha",
        strip=False,
        widget=forms.PasswordInput(attrs={
            "class": "w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/50 focus:outline-none transition",
            "placeholder": "••••••••"
        })
    )
    
    password2 = forms.CharField(
        label="Confirmar senha",
        strip=False,
        widget=forms.PasswordInput(attrs={
            "class": "w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/50 focus:outline-none transition",
            "placeholder": "••••••••"
        })
    )
    
    # Dados da candidatura
    full_name = forms.CharField(
        label="Nome completo",
        max_length=255,
        widget=forms.TextInput(attrs={
            "class": "w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/50 focus:outline-none transition",
            "placeholder": "Seu nome completo"
        })
    )
    
    email = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(attrs={
            "class": "w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/50 focus:outline-none transition",
            "placeholder": "seu@email.com"
        })
    )
    
    phone = forms.CharField(
        label="Telefone",
        max_length=20,
        widget=forms.TextInput(attrs={
            "class": "w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/50 focus:outline-none transition",
            "placeholder": "(00) 00000-0000"
        })
    )
    
    organization = forms.CharField(
        label="Organização",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/50 focus:outline-none transition",
            "placeholder": "Empresa/Instituição"
        })
    )
    
    linkedin_url = forms.URLField(
        label="Perfil LinkedIn",
        required=False,
        widget=forms.URLInput(attrs={
            "class": "w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/50 focus:outline-none transition",
            "placeholder": "https://linkedin.com/in/seuusuario"
        })
    )
    
    certificate = forms.FileField(
        label="Certificado",
        help_text="PDF ou imagem (máx 5MB)",
        widget=forms.FileInput(attrs={
            "class": "w-full text-gray-300",
            "accept": ".pdf,.jpg,.jpeg,.png"
        })
    )
    
    resume = forms.FileField(
        label="Currículo",
        help_text="PDF (máx 5MB)",
        widget=forms.FileInput(attrs={
            "class": "w-full text-gray-300",
            "accept": ".pdf"
        })
    )
    
    justification = forms.CharField(
        label="Por que deseja ser auditor?",
        widget=forms.Textarea(attrs={
            "class": "w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/50 focus:outline-none transition",
            "rows": 5,
            "placeholder": "Descreva sua experiência e motivação..."
        })
    )
    
    terms_accepted = forms.BooleanField(
        label="Aceito os termos e responsabilidades de um auditor",
        widget=forms.CheckboxInput(attrs={
            "class": "w-5 h-5 text-blue-500 bg-white/5 border-white/30 rounded focus:ring-blue-500 focus:ring-offset-gray-900"
        })
    )
    
    class Meta:
        model = User
        fields = ["username", "email"]
    
    def clean_certificate(self):
        """Valida o certificado."""
        certificate = self.cleaned_data.get('certificate')
        if certificate:
            if certificate.size > 5 * 1024 * 1024:
                raise forms.ValidationError("O arquivo deve ter no máximo 5MB.")
            ext = certificate.name.split('.')[-1].lower()
            if ext not in ['pdf', 'jpg', 'jpeg', 'png']:
                raise forms.ValidationError("Apenas PDF ou imagens (JPG, PNG) são permitidos.")
        return certificate
    
    def clean_resume(self):
        """Valida o currículo."""
        resume = self.cleaned_data.get('resume')
        if resume:
            if resume.size > 5 * 1024 * 1024:
                raise forms.ValidationError("O arquivo deve ter no máximo 5MB.")
            ext = resume.name.split('.')[-1].lower()
            if ext != 'pdf':
                raise forms.ValidationError("Apenas arquivos PDF são permitidos.")
        return resume
    
    def clean_terms_accepted(self):
        """Valida que os termos foram aceitos."""
        terms_accepted = self.cleaned_data.get('terms_accepted')
        if not terms_accepted:
            raise forms.ValidationError("Você deve aceitar os termos para se candidatar.")
        return terms_accepted
    
    def clean_linkedin_url(self):
        """Valida URL do LinkedIn."""
        url = self.cleaned_data.get('linkedin_url')
        if url and 'linkedin.com' not in url.lower():
            raise forms.ValidationError("Por favor, insira uma URL válida do LinkedIn.")
        return url
    
    def save(self, commit: bool = True):
        """Salva usuário INATIVO até aprovação da candidatura."""
        user = super().save(commit=False)
        user.email = self.cleaned_data.get("email")
        user.role = User.Roles.PRODUCER  # Temporário, muda para AUDITOR após aprovação
        user.is_active = False  # DESATIVA até admin aprovar
        
        if commit:
            user.save()
            
            # Cria a candidatura vinculada
            application = AuditorApplication.objects.create(
                user=user,
                full_name=self.cleaned_data.get("full_name"),
                email=self.cleaned_data.get("email"),
                phone=self.cleaned_data.get("phone"),
                organization=self.cleaned_data.get("organization", ""),
                linkedin_url=self.cleaned_data.get("linkedin_url", ""),
                certificate=self.cleaned_data.get("certificate"),
                resume=self.cleaned_data.get("resume"),
                justification=self.cleaned_data.get("justification"),
                terms_accepted=self.cleaned_data.get("terms_accepted"),
                status=AuditorApplication.Status.PENDING
            )
        
        return user
