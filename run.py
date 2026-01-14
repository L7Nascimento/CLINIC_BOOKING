"""
Script de inicialização do Sistema de Agendamento
"""
import sys
import os

# Adiciona diretório atual ao Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🔧 Configurando ambiente...")

# Agora importa o resto
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.config import settings
from app.db.session import init_db
from app.telegram.bot import start_bot

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia ciclo de vida da aplicação"""
    logger.info("🚀 Iniciando Sistema de Agendamento Inteligente...")
    
    logger.info("📦 Inicializando banco de dados...")
    init_db()
    logger.info("✅ Banco de dados inicializado!")
    
    logger.info("🤖 Iniciando bot do Telegram...")
    bot_task = asyncio.create_task(asyncio.to_thread(start_bot))
    
    logger.info("✅ Sistema inicializado com sucesso!")
    
    yield
    
    logger.info("🛑 Encerrando sistema...")
    bot_task.cancel()
    logger.info("👋 Sistema encerrado!")

# Criar aplicação FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description="Sistema inteligente de agendamento com IA",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "status": "running",
        "version": "1.0.0",
        "message": "Sistema de Agendamento Inteligente operacional! 🚀"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    
    print(f"🌟 Iniciando {settings.APP_NAME}...")
    print(f"🔧 Modo Debug: {settings.DEBUG}")
    print("="*60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )