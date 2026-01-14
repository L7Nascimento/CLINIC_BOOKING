"""
Inicia apenas o bot do Telegram
"""
import sys
import os

# Adiciona diretório ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🔧 Configurando ambiente...")

# Importa e executa o bot
from app.telegram.bot import start_bot

if __name__ == "__main__":
    print("🤖 Iniciando Bot do Telegram...")
    print("="*60)
    start_bot()