# 🏗️ Arquitetura do Sistema

## 📐 Visão Geral

O Sistema de Agendamento Inteligente é uma aplicação moderna baseada em microserviços que integra:

- **Backend**: FastAPI (Python)
- **Interface**: Telegram Bot
- **IA**: Claude (Anthropic)
- **Banco de Dados**: SQLite/PostgreSQL

```
┌─────────────────────────────────────────────────────────┐
│                    USUÁRIOS                              │
│         (Clientes, Profissionais, Admins)               │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│              TELEGRAM BOT INTERFACE                      │
│  - Comandos (/start, /menu, /help)                      │
│  - Mensagens de texto (conversação natural)             │
│  - Botões inline interativos                            │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│              TELEGRAM HANDLERS                           │
│  - Roteamento de callbacks                              │
│  - Gerenciamento de estado                              │
│  - Processamento de mensagens                           │
└──────────────────┬──────────────────────────────────────┘
                   │
      ┌────────────┴────────────┐
      ▼                         ▼
┌────────────────┐    ┌──────────────────┐
│   AI SERVICE   │    │  CORE SERVICES   │
│                │    │                  │
│ - Claude IA    │    │ - Appointments   │
│ - Conversação  │    │ - Clients        │
│ - Análise      │    │ - Professionals  │
│ - Relatórios   │    │ - Admin          │
└────────────────┘    └──────────────────┘
                             │
                             ▼
                   ┌──────────────────┐
                   │    DATABASE      │
                   │  - Users         │
                   │  - Appointments  │
                   │  - Services      │
                   │  - Messages      │
                   └──────────────────┘
```

## 🔄 Fluxo de Dados

### 1. Agendamento de Cliente

```
Cliente → /start
    ↓
Bot verifica usuário no DB
    ↓
Se novo: Cadastro
Se existente: Menu
    ↓
Cliente: "Quero agendar"
    ↓
IA analisa intenção
    ↓
Sistema mostra serviços
    ↓
Cliente escolhe serviço
    ↓
Sistema mostra profissionais
    ↓
Cliente escolhe profissional
    ↓
Sistema calcula horários disponíveis
    ↓
Cliente escolhe horário
    ↓
Sistema valida:
- Horário disponível?
- Cliente confiável para horário de pico?
    ↓
Agendamento criado
    ↓
Confirmação enviada ao cliente
```

### 2. Conversação com IA

```
Cliente: "Quanto custa um corte?"
    ↓
Handler recebe mensagem
    ↓
Contexto montado:
- Nome do usuário
- Serviços disponíveis
- Agendamentos ativos
- Nível de confiabilidade
    ↓
Enviado para Claude IA
    ↓
IA processa com contexto
    ↓
Resposta elegante gerada
    ↓
Enviada ao cliente
```

### 3. Alertas Automáticos

```
Sistema (Job agendado)
    ↓
Verifica agendamentos próximos
    ↓
Para cada agendamento em 24h:
- Envia alerta ao cliente
- Marca como "alerta_24h_sent"
    ↓
Para cada agendamento em 1h:
- Envia lembrete
- Marca como "alert_1h_sent"
```

## 🗂️ Estrutura de Pastas Detalhada

```
project/
│
├── app/                        # Aplicação principal
│   ├── main.py                 # Entry point (FastAPI + Bot)
│   ├── config.py               # Configurações centralizadas
│   │
│   ├── api/                    # Camada REST (opcional)
│   │   ├── routes/
│   │   │   ├── clients.py      # Endpoints de clientes
│   │   │   ├── professionals.py
│   │   │   ├── admin.py
│   │   │   └── appointments.py
│   │   └── dependencies.py
│   │
│   ├── core/                   # Lógica de Negócio
│   │   ├── client_service.py   # Regras de clientes
│   │   ├── professional_service.py
│   │   ├── admin_service.py
│   │   ├── appointment_service.py
│   │   └── ai_service.py       # Integração Claude
│   │
│   ├── db/                     # Camada de Dados
│   │   ├── models.py           # Modelos SQLAlchemy
│   │   ├── schemas.py          # Pydantic schemas
│   │   └── session.py          # Gestão de sessões
│   │
│   ├── telegram/               # Interface Telegram
│   │   ├── bot.py              # Configuração do bot
│   │   ├── handlers.py         # Lógica de handlers
│   │   └── keyboards.py        # Teclados interativos
│   │
│   └── utils/                  # Utilitários
│       ├── logger.py
│       ├── time_utils.py
│       └── validation.py
│
├── scripts/                    # Scripts auxiliares
│   └── seed_database.py        # Popular DB inicial
│
├── tests/                      # Testes
│   ├── test_clients.py
│   ├── test_appointments.py
│   └── test_ai_service.py
│
├── .env                        # Variáveis de ambiente
├── .env.example
├── requirements.txt
├── README.md
├── QUICK_START.md
└── ARCHITECTURE.md
```

## 🎯 Componentes Principais

### 1. Models (Banco de Dados)

```python
User
├── id (PK)
├── telegram_id (único)
├── name
├── role (CLIENT, PROFESSIONAL, ADMIN)
└── timestamps

ClientProfile
├── id (PK)
├── user_id (FK)
├── no_show_count
├── late_cancellation_count
├── reliability_level
└── preferences

ProfessionalProfile
├── id (PK)
├── user_id (FK)
├── specialty
├── commission_percentage
└── is_available

Appointment
├── id (PK)
├── client_id (FK)
├── professional_id (FK)
├── service_id (FK)
├── scheduled_date
├── status
└── timestamps
```

### 2. AI Service

Responsável por:
- Conversação natural
- Análise de intenções
- Geração de relatórios
- Sugestões inteligentes

**Métodos principais:**
- `chat()` - Conversação geral
- `analyze_appointment_request()` - Extrai dados de agendamento
- `generate_professional_summary()` - Resumo para profissional
- `generate_admin_report()` - Relatório executivo

### 3. Appointment Service

Gerencia todo o ciclo de vida dos agendamentos:
- Criação
- Cancelamento
- Reagendamento
- Validações
- Cálculo de horários disponíveis

**Regras de negócio:**
- Verifica disponibilidade
- Valida confiabilidade para horários de pico
- Atualiza métricas do cliente
- Previne sobreposições

### 4. Telegram Bot

Interface principal do sistema:
- Comandos
- Callbacks de botões
- Gerenciamento de estado
- Teclados interativos

**Estados possíveis:**
- `awaiting_name` - Aguardando nome no cadastro
- `awaiting_message_to_management` - Aguardando mensagem
- `selecting_service` - Escolhendo serviço
- `selecting_professional` - Escolhendo profissional
- `selecting_date` - Escolhendo data
- `selecting_time` - Escolhendo horário

## 🔐 Sistema de Permissões

### Roles (Papéis)

**CLIENT (Cliente)**
- ✅ Agendar horários
- ✅ Cancelar próprios agendamentos
- ✅ Ver próprio histórico
- ✅ Enviar mensagens à gerência
- ❌ Acesso a dados de outros clientes
- ❌ Configurações do sistema

**PROFESSIONAL (Profissional)**
- ✅ Ver própria agenda
- ✅ Adicionar clientes em horários vagos
- ✅ Cancelar agendamentos (com justificativa)
- ✅ Ver próprios ganhos
- ✅ Receber relatórios diários
- ❌ Ver ganhos de outros profissionais
- ❌ Modificar serviços ou preços

**ADMIN (Administrador)**
- ✅ Acesso total ao sistema
- ✅ CRUD completo (Usuários, Serviços, Profissionais)
- ✅ Relatórios gerenciais
- ✅ Configurações globais
- ✅ Precificação de serviços
- ✅ Gerenciar permissões

## 📊 Sistema de Confiabilidade

### Níveis

```python
EXCELLENT (Excelente)
- 0 no-shows
- 0 cancelamentos tardios
- ✅ Pode agendar em qualquer horário

GOOD (Bom)
- 1-2 problemas
- ✅ Pode agendar em qualquer horário

MODERATE (Moderado)
- 3-4 problemas
- ⚠️ Alerta para profissional

LOW (Baixo)
- 5+ problemas
- ❌ NÃO pode agendar em horários de pico
```

### Regras

**Cancelamento Tardio:**
- Menos de 4h antes → Penalizado
- Mais de 4h antes → Sem penalização

**No-Show:**
- Sempre penalizado
- Sistema marca automaticamente

**Horários de Pico:**
- Segunda a Sexta: 18h-20h
- Clientes LOW não podem agendar

## 🔔 Sistema de Alertas

### Tipos de Alertas

**24 horas antes:**
```
📅 Lembrete de Agendamento

Olá, João!

Você tem um agendamento amanhã:
• Corte de Cabelo
• 15/01/2026 às 14:00
• Com: Maria Santos

Confirme sua presença ou reagende se necessário.
```

**1 hora antes:**
```
⏰ Seu agendamento é daqui a 1 hora!

Corte de Cabelo
Hoje às 14:00
Com: Maria Santos

Nos vemos em breve! 😊
```

**Atraso detectado (15 min após horário):**
```
❓ Detectamos que você não chegou

Seu horário era 14:00.
O que deseja fazer?

[⏰ Vou atrasar 15 min]
[⏰ Vou atrasar 30 min]
[🔄 Reagendar]
[❌ Cancelar]
```

## 🚀 Escalabilidade

### Otimizações Implementadas

1. **Cache de Consultas**
   - Serviços ativos em cache
   - Profissionais disponíveis em cache

2. **Índices de Banco**
   - telegram_id (único)
   - scheduled_date
   - status de agendamentos

3. **Queries Eficientes**
   - Eager loading de relacionamentos
   - Filtros em banco, não em memória

### Para Escalar

**Horizontal:**
- Multiple workers do bot
- Load balancer
- Redis para estado compartilhado

**Vertical:**
- PostgreSQL ao invés de SQLite
- Índices adicionais
- Queries otimizadas

## 🔧 Manutenção

### Logs

Todos os eventos importantes são logados:
- Agendamentos criados
- Cancelamentos
- Erros
- Chamadas à API da IA

### Monitoramento

Métricas importantes:
- Taxa de no-shows
- Taxa de cancelamento
- Ocupação por profissional
- Horários mais populares
- Faturamento diário

### Backups

**Banco de Dados:**
```bash
# Backup diário recomendado
cp scheduling.db backups/scheduling_$(date +%Y%m%d).db
```

**Logs:**
- Rotação automática
- Retenção de 30 dias

## 🎨 Personalização

### Mensagens da IA

Edite em `app/core/ai_service.py`:
```python
def _build_system_prompt(self, context):
    base_prompt = """
    Você é [SEU ASSISTENTE]
    
    [SUAS DIRETRIZES]
    """
```

### Teclados

Edite em `app/telegram/keyboards.py`:
```python
def main_menu(role):
    # Personalize os botões
    keyboard = [...]
```

### Regras de Negócio

Edite em `app/config.py`:
```python
CANCELLATION_LIMIT_HOURS = 4
MAX_NO_SHOW_COUNT = 3
BUSINESS_HOURS_START = "08:00"
```

## 📚 Tecnologias e Bibliotecas

### Core
- **Python 3.10+**: Linguagem base
- **FastAPI**: Framework web assíncrono
- **SQLAlchemy**: ORM poderoso
- **Pydantic**: Validação de dados

### Telegram
- **python-telegram-bot 20.7**: Bot framework moderno
- Suporta: comandos, callbacks, inline keyboards

### IA
- **anthropic**: SDK oficial da Anthropic
- **Claude Sonnet 4**: Modelo de IA usado

### Database
- **SQLite**: Desenvolvimento
- **PostgreSQL**: Produção (recomendado)

---

**Próximos passos:** Leia o QUICK_START.md para começar a usar o sistema!