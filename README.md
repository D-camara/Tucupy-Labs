# 🌱 EcoTrade - Marketplace de Créditos de Carbono

Sistema de marketplace regional para compra e venda de créditos de carbono com validação por auditores.

## 📋 Visão Geral

EcoTrade conecta produtores de créditos de carbono com empresas interessadas em compensar suas emissões, através de uma plataforma segura com sistema de validação por auditores certificados.

### Principais Funcionalidades

- 🔐 **Sistema de Autenticação com Roles** (Produtor, Empresa, Auditor, Admin)
- 📊 **Dashboard Personalizado** por tipo de usuário
- 🌿 **Marketplace de Créditos** com listagens ativas
- ✅ **Sistema de Validação por Auditores** antes da listagem
- 💰 **Transações Seguras** com histórico completo
- 📧 **Notificações por Email** para eventos importantes
- 🎨 **Interface Moderna** com TailwindCSS 4.x
- 📱 **Design Responsivo** para todos os dispositivos

## 🚀 Stack Tecnológica

- **Backend**: Django 5.2.7
- **Python**: 3.11+
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Frontend**: TailwindCSS 4.x via django-tailwind-4[reload]
- **Email**: Gmail SMTP
- **File Uploads**: Django Media Files

## 📁 Estrutura do Projeto

```
ecotrade/
├── accounts/          # Autenticação, usuários, auditores
├── credits/           # Créditos de carbono, marketplace
├── transactions/      # Compras e histórico
├── dashboard/         # Dashboard personalizado
├── theme/             # TailwindCSS configuração
├── templates/         # Templates globais
├── docs/              # Documentação adicional
│   ├── setup/        # Guias de configuração
│   └── testing/      # Planos de teste
└── ecotrade/          # Configuração Django
```

## ⚙️ Setup do Ambiente

### Pré-requisitos

- Python 3.11 ou superior
- Node.js 18+ (para Tailwind)
- Git

### Instalação

1. **Clone o repositório**
```bash
git clone https://github.com/D-camara/Tucupy-Labs.git
cd Tucupy-Labs
```

2. **Crie e ative o ambiente virtual**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Instale as dependências Python**
```bash
pip install -r requirements.txt
```

4. **Configure as variáveis de ambiente**
```bash
cp .env.example .env
# Edite o .env com suas configurações
```

5. **Execute as migrações**
```bash
python manage.py migrate
```

6. **Crie um superusuário**
```bash
python manage.py createsuperuser
```

7. **Instale o Tailwind**
```bash
python manage.py tailwind install
```

8. **Carregue dados de teste (opcional)**
```bash
python manage.py seed_users
python manage.py seed_credits
python manage.py seed_listings
```

## 🏃 Executando o Projeto

### Desenvolvimento

**Opção 1: Comando único (recomendado)**
```bash
python manage.py tailwind dev
```
Este comando inicia Django + Tailwind + auto-reload simultaneamente.

**Opção 2: Comandos separados**

Terminal 1 - Django:
```bash
python manage.py runserver
```

Terminal 2 - Tailwind:
```bash
python manage.py tailwind start
```

Acesse: `http://localhost:8000`

## 🧪 Testes

Execute todos os testes:
```bash
python manage.py test
```

Testes por app:
```bash
python manage.py test accounts
python manage.py test credits
python manage.py test transactions
python manage.py test dashboard
```

## 👥 Roles e Permissões

### 🌾 Produtor (PRODUCER)
- Criar créditos de carbono
- Listar créditos para venda (após aprovação)
- Ver histórico de vendas
- Gerenciar carteira de créditos

### 🏢 Empresa (COMPANY)
- Navegar marketplace
- Comprar créditos
- Ver histórico de compras
- Adicionar saldo virtual

### ✅ Auditor (AUDITOR)
- Revisar créditos pendentes
- Aprovar ou rejeitar créditos
- Ver histórico de validações
- Adicionar notas técnicas

### 👨‍💼 Admin (ADMIN)
- Aprovar candidaturas de auditores
- Gerenciar usuários
- Acesso ao Django Admin
- Visualizar estatísticas globais

## 🔄 Fluxo de Negócio

1. **Produtor cria crédito** → Status: `PENDING`
2. **Auditor revisa** → Status: `UNDER_REVIEW`
3. **Auditor aprova** → Status: `APPROVED`
4. **Produtor lista no marketplace** → Status: `LISTED`
5. **Empresa compra** → Transação criada
6. **Transferência de propriedade** → Status: `SOLD`

## 📧 Configuração de Email

O sistema envia emails para:
- Confirmação de registro
- Candidatura de auditor recebida
- Aprovação/Rejeição de candidatura
- Validação de crédito (aprovado/rejeitado)

Ver: `docs/setup/EMAIL_SETUP.md` para configuração detalhada.

## 🎨 Customização Visual

### Cores do Tema
- **Primary**: Tucupi Green (`#10b981`, `#059669`)
- **Secondary**: Tucupi Accent (`#3b82f6`)
- **Background**: Dark gradient

### Tailwind Config
- Config: `theme/static_src/tailwind.config.js`
- Styles: `theme/static_src/src/styles.css`

## 📚 Documentação Adicional

- **CLAUDE.md** - Arquitetura e overview completo
- **PLAN.md** - Plano de implementação por fases
- **AGENTS.md** - Guia para agentes AI
- **CHANGELOG.md** - Histórico de mudanças
- **docs/testing/** - Planos e guias de teste

## 🐛 Troubleshooting

### Tailwind não compila
```bash
python manage.py tailwind install
python manage.py tailwind build
```

### Erros de migração
```bash
python manage.py migrate --run-syncdb
```

### Port 8000 já em uso
```bash
python manage.py runserver 8080
```

## 🤝 Contribuindo

1. Crie uma branch para sua feature: `git checkout -b feature/nova-funcionalidade`
2. Commit suas mudanças: `git commit -m 'feat: adiciona nova funcionalidade'`
3. Push para a branch: `git push origin feature/nova-funcionalidade`
4. Abra um Pull Request para `dev`

### Convenção de Commits

- `feat:` - Nova funcionalidade
- `fix:` - Correção de bug
- `docs:` - Documentação
- `style:` - Formatação
- `refactor:` - Refatoração
- `test:` - Testes
- `chore:` - Manutenção

## 📝 Management Commands Úteis

```bash
# Usuários
python manage.py seed_users                    # Criar usuários de teste
python manage.py add_balance <user> <amount>   # Adicionar saldo

# Créditos
python manage.py seed_credits                  # Criar créditos de teste
python manage.py seed_listings                 # Criar listings de teste

# Transações
python manage.py seed_transactions             # Criar transações de teste
```

## 📊 Status do Projeto

- ✅ Autenticação e RBAC
- ✅ Dashboard personalizado
- ✅ Marketplace de créditos
- ✅ Sistema de validação por auditores
- ✅ Transações e histórico
- ✅ Notificações por email
- ✅ Interface moderna com Tailwind
- ⏳ Relatórios e análises (futuro)
- ⏳ API REST (futuro)
- ⏳ Integração com blockchain (futuro)

## 📄 Licença

Este projeto está sob a licença MIT. Ver arquivo LICENSE para mais detalhes.

## 👨‍💻 Desenvolvido por

**Tucupy Labs**  
Marketplace Regional de Créditos de Carbono

---

**Branch Atual**: `Validação-de-créditos`  
**Última Atualização**: Outubro 2025
