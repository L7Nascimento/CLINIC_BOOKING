"""
Script para criar automaticamente toda a estrutura do projeto
Execute: python setup_project.py
"""

import os
from pathlib import Path

# Definir estrutura de diretórios
DIRECTORIES = [
    "app",
    "app/api",
    "app/api/routes",
    "app/core",
    "app/db",
    "app/telegram",
    "app/utils",
    "scripts",
    "tests",
]

# Definir arquivos vazios (__init__.py)
INIT_FILES = [
    "app/__init__.py",
    "app/api/__init__.py",
    "app/api/routes/__init__.py",
    "app/core/__init__.py",
    "app/db/__init__.py",
    "app/telegram/__init__.py",
    "app/utils/__init__.py",
    "scripts/__init__.py",
    "tests/__init__.py",
]

# Conteúdos dos arquivos (copiados dos artifacts)
FILES_CONTENT = {
    "requirements.txt": """# FastAPI e servidor
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0

# Banco de dados
sqlalchemy==2.0.25
alembic==1.13.1

# Telegram Bot
python-telegram-bot==20.7

# Claude IA
anthropic==0.18.1

# Utilidades
python-dotenv==1.0.0
python-multipart==0.0.6
httpx==0.26.0

# Data e hora
python-dateutil==2.8.2
pytz==2023.3

# Validação e parsing
email-validator==2.1.0

# Testes
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0

# Desenvolvimento
black==24.1.1
flake8==7.0.0
mypy==1.8.0
""",

    ".env.example": """# Configurações do Sistema de Agendamento

# Database
DATABASE_URL=sqlite:///./scheduling.db
# Para PostgreSQL: postgresql://user:password@localhost/dbname

# Telegram Bot
TELEGRAM_BOT_TOKEN=seu_token_aqui
# Obtenha em: https://t.me/BotFather

# Anthropic Claude API
ANTHROPIC_API_KEY=sua_chave_aqui
# Obtenha em: https://console.anthropic.com/

# Configurações da Aplicação
DEBUG=True
APP_NAME=Sistema de Agendamento Inteligente

# Regras de Negócio
CANCELLATION_LIMIT_HOURS=4
MAX_NO_SHOW_COUNT=3
ALERT_BEFORE_APPOINTMENT_HOURS=24
REMINDER_BEFORE_APPOINTMENT_MINUTES=60

# Horários de Funcionamento
BUSINESS_HOURS_START=08:00
BUSINESS_HOURS_END=20:00
""",

    ".gitignore": """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv

# Database
*.db
*.sqlite
*.sqlite3

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Testing
.pytest_cache/
.coverage
htmlcov/
""",

    "README.md": """# 🤖 Sistema de Agendamento Inteligente com IA

Sistema completo de agendamento para clínicas, salões e barbearias integrado com Telegram e Claude IA.

## 🚀 Instalação Rápida

```bash
# 1. Instale dependências
pip install -r requirements.txt

# 2. Configure variáveis de ambiente
cp .env.example .env
# Edite .env com seus tokens

# 3. Inicialize o banco
python scripts/seed_database.py

# 4. Execute
python app/main.py
```

## 📚 Documentação

- **QUICK_START.md** - Guia de início rápido
- **ARCHITECTURE.md** - Documentação da arquitetura

## ✨ Funcionalidades

- ✅ Agendamento inteligente com IA
- ✅ Interface via Telegram
- ✅ Sistema de confiabilidade
- ✅ Alertas automáticos
- ✅ Relatórios gerenciais

## 🔑 Configuração

1. Crie bot no Telegram: @BotFather
2. Obtenha API Key: https://console.anthropic.com/
3. Configure no arquivo .env

---
Desenvolvido com ❤️ usando Python e Claude IA
"""
}

def create_project_structure():
    """Cria toda a estrutura do projeto"""
    
    base_dir = Path("scheduling-system")
    
    print("🚀 Criando Sistema de Agendamento Inteligente...")
    print("=" * 60)
    
    # Criar diretório base
    if base_dir.exists():
        print(f"⚠️  Diretório '{base_dir}' já existe!")
        response = input("Deseja sobrescrever? (s/n): ")
        if response.lower() != 's':
            print("❌ Operação cancelada.")
            return
        print("🗑️  Removendo diretório existente...")
        import shutil
        shutil.rmtree(base_dir)
    
    base_dir.mkdir(exist_ok=True)
    print(f"✅ Diretório base criado: {base_dir}")
    
    # Criar subdiretórios
    print("\n📁 Criando estrutura de diretórios...")
    for directory in DIRECTORIES:
        dir_path = base_dir / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {directory}/")
    
    # Criar arquivos __init__.py
    print("\n📄 Criando arquivos __init__.py...")
    for init_file in INIT_FILES:
        file_path = base_dir / init_file
        file_path.touch()
        print(f"  ✓ {init_file}")
    
    # Criar arquivos com conteúdo
    print("\n📝 Criando arquivos de configuração...")
    for filename, content in FILES_CONTENT.items():
        file_path = base_dir / filename
        file_path.write_text(content, encoding='utf-8')
        print(f"  ✓ {filename}")
    
    # Criar arquivo de instruções
    instructions = """
# 📋 PRÓXIMOS PASSOS

Seu projeto foi criado com sucesso! Agora siga estes passos:

## 1️⃣ Copiar Código dos Artifacts

Você precisa copiar o código dos artifacts do Claude para os arquivos:

### Arquivos principais (COPIE DOS ARTIFACTS):

- app/config.py (artifact: config_file)
- app/main.py (artifact: main_file)
- app/db/models.py (artifact: db_models)
- app/db/session.py (artifact: db_session)
- app/core/ai_service.py (artifact: ai_service)
- app/core/appointment_service.py (artifact: appointment_service)
- app/telegram/bot.py (artifact: telegram_bot)
- app/telegram/handlers.py (artifact: telegram_handlers)
- app/telegram/keyboards.py (artifact: telegram_keyboards)
- scripts/seed_database.py (artifact: seed_database)

## 2️⃣ Configurar Ambiente

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente
# Windows:
venv\\Scripts\\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

## 3️⃣ Configurar Tokens

```bash
# Copiar exemplo de configuração
cp .env.example .env

# Editar .env e adicionar:
# - TELEGRAM_BOT_TOKEN (obtenha em @BotFather)
# - ANTHROPIC_API_KEY (obtenha em console.anthropic.com)
```

## 4️⃣ Inicializar e Executar

```bash
# Popular banco de dados
python scripts/seed_database.py

# Executar sistema
python app/main.py
```

## ✅ Verificação

Seu projeto deve ter esta estrutura:

scheduling-system/
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
├── NEXT_STEPS.txt (este arquivo)
├── app/
│   ├── config.py (COPIE DO ARTIFACT)
│   ├── main.py (COPIE DO ARTIFACT)
│   ├── core/
│   ├── db/
│   └── telegram/
└── scripts/
    └── seed_database.py (COPIE DO ARTIFACT)

## 🆘 Precisa de Ajuda?

Consulte os artifacts da conversa com Claude para o código completo.
    """
    
    next_steps_path = base_dir / "NEXT_STEPS.txt"
    next_steps_path.write_text(instructions, encoding='utf-8')
    
    # Resumo final
    print("\n" + "=" * 60)
    print("✅ Estrutura do projeto criada com sucesso!")
    print("=" * 60)
    print(f"\n📂 Local: {base_dir.absolute()}")
    print(f"\n📋 Próximos passos:")
    print(f"  1. Entre no diretório: cd {base_dir}")
    print(f"  2. Leia o arquivo: NEXT_STEPS.txt")
    print(f"  3. Copie o código dos artifacts do Claude")
    print(f"  4. Configure o .env")
    print(f"  5. Execute: python scripts/seed_database.py")
    print(f"\n💡 Dica: Todos os artifacts estão na conversa com Claude!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        create_project_structure()
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()