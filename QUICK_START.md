# 🚀 Guia de Início Rápido

Este guia vai te ajudar a colocar o sistema funcionando em **menos de 10 minutos**!

## ⚡ Configuração Rápida (5 passos)

### 1️⃣ Instale as dependências

```bash
# Clone o repositório
git clone <seu-repo>
cd project

# Crie ambiente virtual
python -m venv venv

# Ative o ambiente
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instale dependências
pip install -r requirements.txt
```

### 2️⃣ Crie seu bot no Telegram

1. Abra o Telegram
2. Procure por `@BotFather`
3. Envie: `/newbot`
4. Escolha um nome: `Meu Salão Bot`
5. Escolha um username: `meusalaobot` (deve terminar com 'bot')
6. **COPIE O TOKEN** que ele fornecer!

### 3️⃣ Obtenha sua API Key da Anthropic (Claude)

1. Acesse: https://console.anthropic.com/
2. Faça login ou crie conta
3. Vá em "API Keys"
4. Clique em "Create Key"
5. **COPIE A CHAVE**

### 4️⃣ Configure o arquivo .env

```bash
# Copie o exemplo
cp .env.example .env

# Edite o .env e preencha:
TELEGRAM_BOT_TOKEN=seu_token_do_botfather_aqui
ANTHROPIC_API_KEY=sua_chave_anthropic_aqui
```

### 5️⃣ Inicialize e execute!

```bash
# Popular banco de dados com dados de exemplo
python scripts/seed_database.py

# Executar sistema
python app/main.py
```

**Pronto! 🎉** Seu bot já está funcionando!

## 📱 Testando o Bot

1. Abra o Telegram
2. Procure pelo username do seu bot (ex: `@meusalaobot`)
3. Clique em "Start" ou envie `/start`
4. Siga as instruções para se cadastrar

### Comandos Disponíveis

- `/start` - Iniciar bot
- `/menu` - Ver menu principal
- `/help` - Ver ajuda

### Teste a Conversação Natural

Envie mensagens como:
- "Olá!"
- "Quais serviços vocês têm?"
- "Quero agendar um corte de cabelo"
- "Quanto custa?"

## 🔧 Obtendo seu Telegram ID

Para se tornar admin, você precisa do seu Telegram ID:

1. No Telegram, procure por `@userinfobot`
2. Envie `/start`
3. Ele mostrará seu ID (ex: `123456789`)
4. **COPIE ESSE NÚMERO**

### Tornando-se Admin

Execute este código Python:

```python
from app.db.session import SessionLocal
from app.db.models import User, UserRole

db = SessionLocal()

# Substitua SEU_TELEGRAM_ID pelo número que você copiou
admin = User(
    telegram_id="SEU_TELEGRAM_ID",
    name="Seu Nome",
    role=UserRole.ADMIN,
    email="seu@email.com"
)

db.add(admin)
db.commit()
db.close()

print("✅ Admin criado!")
```

Ou edite diretamente o `scripts/seed_database.py` e execute novamente.

## 🎯 Próximos Passos

### Personalize os Serviços

1. Abra `scripts/seed_database.py`
2. Edite a lista `services_data`
3. Execute: `python scripts/seed_database.py`

### Adicione Profissionais

No código acima, edite `professionals_data` com seus profissionais reais.

### Teste Funcionalidades

**Como Cliente:**
1. Abra o bot no Telegram
2. Envie `/start` para se cadastrar
3. Teste: "Quero agendar um horário"
4. Navegue pelos menus interativos

**Como Admin:**
1. Configure seu usuário como admin (veja acima)
2. Envie `/menu`
3. Explore: Gerenciar Usuários, Serviços, Relatórios

## 🐛 Problemas Comuns

### Bot não responde

- ✅ Verifique se `python app/main.py` está rodando
- ✅ Confirme que o TOKEN está correto no `.env`
- ✅ Veja os logs no terminal

### Erro de API da Anthropic

- ✅ Verifique se a ANTHROPIC_API_KEY está correta
- ✅ Confirme que tem créditos na conta Anthropic
- ✅ Teste a chave em: https://console.anthropic.com/

### Erro de Banco de Dados

```bash
# Delete e recrie o banco
rm scheduling.db
python scripts/seed_database.py
```

## 📊 Recursos Avançados

### Horários de Funcionamento

Edite no `.env`:
```
BUSINESS_HOURS_START=08:00
BUSINESS_HOURS_END=20:00
```

### Regras de Cancelamento

```
CANCELLATION_LIMIT_HOURS=4  # Mínimo de 4h para cancelar
MAX_NO_SHOW_COUNT=3  # Máximo de faltas permitidas
```

## 🎨 Personalizando Mensagens

As mensagens do bot estão em:
- `app/core/ai_service.py` - Prompts da IA
- `app/telegram/handlers.py` - Mensagens de resposta
- `app/telegram/keyboards.py` - Textos dos botões

## 📞 Suporte

Problemas? Dúvidas?

1. Verifique os logs no terminal
2. Revise este guia
3. Abra uma issue no GitHub
4. Consulte o README.md completo

## ✅ Checklist de Sucesso

- [ ] Bot responde no Telegram
- [ ] Conseguiu se cadastrar como cliente
- [ ] Viu a lista de serviços
- [ ] Criou usuário admin
- [ ] Sistema de agendamento funciona
- [ ] IA responde perguntas

**Tudo funcionando? Parabéns! 🎉**

Agora você tem um sistema completo de agendamento com IA!

---

**Dica Final:** Explore a conversação natural com o bot. A IA Claude é poderosa e entende contexto. Experimente fazer perguntas complexas!