# 🌐 API Pública EcoTrade

## Visão Geral

API RESTful pública para consulta de créditos de carbono registrados no EcoTrade.
Promove **transparência** permitindo que qualquer pessoa consulte créditos aprovados.

## 📍 Base URL

```
http://localhost:8000/api/
```

## 🔓 Autenticação

A API é **pública** e não requer autenticação. Todos os endpoints retornam apenas dados de créditos **aprovados** por auditores.

## 📚 Documentação Interativa

Acesse a documentação completa com interface para testar os endpoints:

**[http://localhost:8000/api/](http://localhost:8000/api/)**

## 🛠️ Endpoints

### 1. Estatísticas Gerais

```http
GET /api/stats/
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "total_credits_registered": 45,
    "total_co2_amount": 12500.75,
    "credits_available": 20,
    "credits_listed": 15,
    "credits_sold": 10,
    "total_producers": 12,
    "total_companies": 8,
    "total_transactions": 10
  }
}
```

### 2. Lista de Créditos

```http
GET /api/credits/
```

**Parâmetros de query:**
- `status` (opcional): Filtrar por status (`AVAILABLE`, `LISTED`, `SOLD`)
- `validation_status` (opcional): Filtrar por status de validação
- `limit` (opcional): Número de resultados (padrão: 100, máx: 500)
- `offset` (opcional): Paginação (pular N resultados)

**Exemplo:**
```http
GET /api/credits/?status=LISTED&limit=10&offset=0
```

**Resposta:**
```json
{
  "success": true,
  "count": 10,
  "total": 45,
  "limit": 10,
  "offset": 0,
  "next_offset": 10,
  "data": [
    {
      "id": 1,
      "amount": 100.50,
      "unit": "tons CO2",
      "generation_date": "2025-10-15",
      "status": "LISTED",
      "validation_status": "APPROVED",
      "owner_type": "PRODUCER",
      "is_validated": true,
      "validated_at": "2025-10-20T10:30:00Z",
      "created_at": "2025-10-15T08:00:00Z"
    }
  ]
}

⚠️ **Privacidade:** Origem, nomes de usuários e informações identificáveis foram removidas para proteger a privacidade dos participantes.
```

### 3. Detalhe de Crédito

```http
GET /api/credits/{id}/
```

**Exemplo:**
```http
GET /api/credits/1/
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "amount": 100.50,
    "unit": "tons CO2",
    "generation_date": "2025-10-15",
    "status": "LISTED",
    "validation_status": "APPROVED",
    "is_verified": true,
    "owner_type": "PRODUCER",
    "is_validated": true,
    "validated_at": "2025-10-20T10:30:00Z",
    "created_at": "2025-10-15T08:00:00Z"
  }
}

⚠️ **Privacidade:** Dados identificáveis (origem, nomes, notas do auditor) foram removidos para proteger a privacidade.
```

**Erro (crédito não encontrado ou não aprovado):**
```json
{
  "success": false,
  "error": "Crédito não encontrado ou não disponível publicamente."
}
```

## 💻 Exemplos de Uso

### Python

```python
import requests

# Estatísticas gerais
response = requests.get('http://localhost:8000/api/stats/')
stats = response.json()
print(f"Total CO2: {stats['data']['total_co2_amount']} tons")

# Listar créditos disponíveis
response = requests.get('http://localhost:8000/api/credits/', params={
    'status': 'LISTED',
    'limit': 5
})
credits = response.json()
for credit in credits['data']:
    print(f"{credit['origin']}: {credit['amount']} {credit['unit']}")

# Detalhe de um crédito
response = requests.get('http://localhost:8000/api/credits/1/')
credit = response.json()
if credit['success']:
    print(f"Crédito validado por: {credit['data']['validated_by']['username']}")
```

### JavaScript (Fetch API)

```javascript
// Estatísticas
fetch('/api/stats/')
  .then(res => res.json())
  .then(data => {
    console.log('Total CO2:', data.data.total_co2_amount);
  });

// Listar créditos
fetch('/api/credits/?status=LISTED&limit=10')
  .then(res => res.json())
  .then(data => {
    data.data.forEach(credit => {
      console.log(`${credit.origin}: ${credit.amount} ${credit.unit}`);
    });
  });

// Detalhe de crédito
fetch('/api/credits/1/')
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      console.log('Crédito:', data.data);
    }
  });
```

### cURL

```bash
# Estatísticas
curl http://localhost:8000/api/stats/

# Listar créditos
curl "http://localhost:8000/api/credits/?status=LISTED&limit=5"

# Detalhe de crédito
curl http://localhost:8000/api/credits/1/
```

## 🔐 Segurança e Privacidade

- ✅ Apenas créditos **aprovados** são expostos
- ✅ Créditos **deletados** (soft-delete) não aparecem
- ✅ Dados sensíveis (emails, telefones) **não** são incluídos
- ✅ Limite máximo de 500 resultados por requisição
- ✅ API pública não requer autenticação

## 📊 Casos de Uso

1. **Dashboards externos**: Criar visualizações de dados em tempo real
2. **Análise de mercado**: Estudar tendências de preços e volumes
3. **Integração com apps**: Desenvolver aplicativos mobile/web
4. **Transparência**: Permitir que o público verifique créditos
5. **Auditoria**: Facilitar verificação por órgãos reguladores

## 🚀 Testando a API

### Usando o navegador

Acesse **[http://localhost:8000/api/](http://localhost:8000/api/)** para:
- Ver documentação completa
- Testar endpoints diretamente
- Copiar URLs de exemplo
- Ver respostas formatadas

### Usando ferramentas

- **Postman**: Importe a collection (disponível na pasta `/docs`)
- **Insomnia**: Teste os endpoints manualmente
- **Thunder Client** (VS Code): Use a extensão

## 📝 Notas

- Todos os timestamps estão em formato ISO 8601
- Valores monetários e quantidades são números decimais
- A API retorna sempre JSON
- Status HTTP: 200 (sucesso), 404 (não encontrado), 400 (erro de validação)

## 🎯 Roadmap

- [ ] Versionamento da API (v1, v2)
- [ ] Rate limiting (proteção contra abuso)
- [ ] Webhooks para notificações
- [ ] Autenticação opcional para dados detalhados
- [ ] GraphQL endpoint
- [ ] SDK em Python e JavaScript

## 📞 Suporte

Para dúvidas ou sugestões sobre a API:
- GitHub Issues: [github.com/D-camara/Tucupy-Labs/issues](https://github.com/D-camara/Tucupy-Labs/issues)
- Email: tucupilabs@gmail.com

---

**Desenvolvido para o Hackathon EcoTrade 2025** 🌱
