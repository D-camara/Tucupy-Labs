# Backlog de Hoje (D-1)

Este arquivo reúne as 5 tarefas básicas para entregar hoje. Mantenha o foco no essencial para deixar o fluxo principal utilizável.

## 1) UI base com Tailwind
- Instalar e configurar `django-tailwind` e criar app `theme`.
- Configurar `tailwind.config.js` e `styles.css`.
- Criar `base.html` e componentes mínimos (`templates/components/navbar.html`, `credit_card.html`).
- Aplicar layout no `dashboard/index.html`.

Entrega: aplicação renderizando com Tailwind e layout base.

## 2) Autenticação e Perfil
- Implementar `/accounts/register`, `/accounts/login`, `/accounts/logout`.
- Implementar `/accounts/profile` (editar `Profile`).
- Incluir URLs de `accounts` no `ecotrade/urls.py`.
- Criar mixins/decorators simples para RBAC (Producer/Company) e usar nas views novas.

Entrega: usuários conseguem criar conta, autenticar e editar perfil.

## 3) Créditos e Marketplace
- Producer-only: criar crédito em `/credits/create`.
- Criar `CreditListing` e marcar `CarbonCredit.status=LISTED` ao listar.
- Marketplace em `/credits/` (listar apenas listings ativos com paginação).
- Detalhe do crédito em `/credits/<id>/`.
- Incluir URLs de `credits` no root.

Entrega: produtor consegue cadastrar e listar, empresa consegue navegar e ver detalhes.

## 4) Transações essenciais
- Company-only: iniciar compra em `/credits/<id>/buy` (POST seguro).
- Completar transação (serviço atômico) e transferir propriedade do crédito para o comprador; atualizar status apropriado.
- Histórico do usuário em `/transactions/` (compras e vendas).
- Incluir URLs de `transactions` no root.

Entrega: fluxo de compra básico concluído de ponta a ponta.

## 5) Dashboard, Admin e QA mínimo
- Dashboard por papel: métricas/resumos básicos (minha carteira, últimas compras/vendas).
- Registrar models no admin com `list_display` útil.
- Testes mínimos: models principais + 1 fluxo e2e (criar crédito → listar → comprar → transferir).
- Atualizar `CHANGELOG.md` e marcar status no `PLAN.md`.

Entrega: visão inicial por papel, admin utilizável e sanidade de testes.

---

Observações rápidas
- Evitar ouro de tolo na UI; manter foco funcional.
- Se compra parcial for necessária, registrar como escopo extra e seguir full-purchase hoje.
- Caso Tailwind no Windows demande ajustes, priorizar base.html + templates e voltar ao tema depois.
