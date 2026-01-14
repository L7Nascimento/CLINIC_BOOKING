# 🤖 Sistema de Agendamento Inteligente com IA

Sistema completo de agendamento para clínicas, salões e barbearias, integrado com Telegram e Claude IA para atendimento automatizado e elegante.

## ✨ Características Principais

### 👥 Para Clientes
- ✅ Cadastro automático via Telegram
- 📅 Agendamento inteligente com sugestões de IA
- 💬 Conversação natural com assistente virtual
- 🔔 Alertas automáticos de agendamentos
- ⏰ Opções de reagendamento em caso de atraso
- 📊 Sistema de confiabilidade (previne no-shows)
- 💌 Envio de mensagens para gerência

### 👨‍💼 Para Profissionais
- 📊 Panorama diário da agenda via IA
- 📈 Relatórios semanais automáticos
- ➕ Adicionar clientes em horários vagos
- ❌ Cancelamento com justificativa
- 💰 Visualização de ganhos e faturamento
- 🔔 Alertas de agendamentos próximos

### 🔐 Para Administradores
- 👥 Gerenciamento completo de usuários e profissionais
- 💼 CRUD de serviços e precificação
- 📊 Relatórios gerenciais com insights de IA
- 💰 Dashboard de faturamento (dia/semana/mês/ano)
- 🎯 Sistema de permissões
- 📈 Análise de performance do negócio

## 🛠️ Tecnologias

- **Python 3.10+** - Linguagem principal
- **FastAPI** - Framework web moderno
- **SQLAlchemy** - ORM para banco de dados
- **python-telegram-bot** - Integração com Telegram
- **Anthropic Claude API** - Inteligência Artificial
- **SQLite/PostgreSQL** - Banco de dados

## 📦 Instalação

### 1. Clone o repositório

```bash
git clone <seu-repositorio>
cd project
```

### 2. Crie ambiente virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instale dependências

```bash
pip install -r requirements.txt
```

### 4. Configure variáveis de ambiente

```bash
cp .env.example .env
```

Edite o arquivo `.env` e preencha:
- `TELEGRAM_BOT_TOKEN` - Token do seu bot (obtenha em @BotFather)
- `ANTHROPIC_API_KEY` - Sua chave da API Claude (obtenha em console.anthropic.com)

### 5. Inicialize o banco de dados

```bash
python -c "from app.db.session import init_db; init_db()"
```

### 6. Execute a aplicação

```bash
python app/main.py
```

O sistema estará rodando em:
- API: http://localhost:8000
- Bot Telegram: Ativo e aguardando mensagens
- Docs: http://localhost:8000/docs

## 🚀 Primeiros Passos

### Criando o Bot no Telegram

1. Abra o Telegram e procure por `@BotFather`
2. Envie `/newbot`
3. Escolha um nome e username para seu bot
4. Copie o token fornecido e cole no `.env`

### Obtendo API Key da Anthropic

1. Acesse https://console.anthropic.com/
2. Crie uma conta ou faça login
3. Vá em "API Keys"
4. Crie uma nova chave
5. Copie e cole no `.env`

### Criando Primeiro Admin

Execute o script de criação de admin:

```python
from app.db.session import SessionLocal
from app.db.models import User, UserRole

db = SessionLocal()

admin = User(
    telegram_id="SEU_TELEGRAM_ID",  # Obtenha com @userinfobot
    name="Admin",
    role=UserRole.ADMIN
)

db.add(admin)
db.commit()
```

## 📱 Usando o Sistema

### Comandos do Telegram

- `/start` - Iniciar bot e cadastro
- `/menu` - Mostrar menu principal
- `/help` - Ajuda e comandos
- `/cancelar` - Cancelar operação atual

### Conversação Natural

O bot entende linguagem natural! Experimente:

- "Quero agendar um corte de cabelo"
- "Quais horários disponíveis amanhã?"
- "Preciso cancelar meu agendamento"
- "Quanto custa uma barba?"

## 🎯 Sistema de Confiabilidade

O sistema rastreia o comportamento dos clientes:

- **Excelente** 🟢 - Nenhuma falta
- **Bom** 🔵 - 1-2 faltas
- **Moderado** 🟡 - 3-4 faltas
- **Baixo** 🔴 - 5+ faltas

Clientes com baixa confiabilidade não podem agendar em horários de pico (18h-20h).

## 📊 Relatórios e IA

O sistema usa Claude IA para:

- 💬 Atendimento conversacional elegante
- 📈 Análise de intenções do usuário
- 📊 Geração de relatórios executivos
- 🎯 Sugestões de melhorias para o negócio
- 📝 Resumos personalizados para profissionais

## 🔒 Segurança

- ✅ Validação de usuários por Telegram ID
- ✅ Sistema de permissões por role
- ✅ Proteção contra no-shows
- ✅ Limite de cancelamentos tardios
- ✅ Logs de todas as operações

## 🗂️ Estrutura do Projeto

```
project/
├── app/
│   ├── main.py              # Entry point
│   ├── config.py            # Configurações
│   ├── core/                # Lógica de negócio
│   │   ├── ai_service.py    # Integração Claude IA
│   │   └── appointment_service.py
│   ├── db/                  # Banco de dados
│   │   ├── models.py        # Modelos SQLAlchemy
│   │   └── session.py       # Configuração DB
│   └── telegram/            # Bot Telegram
│       ├── bot.py           # Bot principal
│       ├── handlers.py      # Handlers de mensagens
│       └── keyboards.py     # Teclados interativos
├── requirements.txt
├── .env.example
└── README.md
```

## 🔧 Desenvolvimento

### Executar testes

```bash
pytest tests/ -v
```

### Formatar código

```bash
black app/
```

### Verificar estilo

```bash
flake8 app/
```

## 🚀 Deploy

### Com Docker (Recomendado)

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app/main.py"]
```

```bash
docker build -t scheduling-bot .
docker run -d --env-file .env -p 8000:8000 scheduling-bot
```

### Deploy em VPS

1. Configure um servidor (DigitalOcean, AWS, etc)
2. Clone o repositório
3. Configure `.env`
4. Use systemd ou supervisor para manter rodando
5. Configure nginx como reverse proxy (opcional)

## 📝 TODO / Próximas Funcionalidades

- [ ] Sistema de pagamentos integrado
- [ ] Lembretes via WhatsApp
- [ ] Dashboard web para admin
- [ ] Integração com Google Calendar
- [ ] Sistema de fidelidade/pontos
- [ ] Avaliações de serviços
- [ ] Multi-idioma
- [ ] Relatórios em PDF

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT.

## 📞 Suporte

Para dúvidas ou suporte:
- Abra uma issue no GitHub
- Entre em contato via Telegram

---

Desenvolvido com ❤️ usando Python e Claude IA