"""
Sistema de Agendamento Inteligente
Aplicação principal que integra FastAPI + Telegram Bot + Claude IA
"""

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
    # Startup
    logger.info("🚀 Iniciando Sistema de Agendamento Inteligente...")
    
    # Inicializa banco de dados
    logger.info("📦 Inicializando banco de dados...")
    init_db()
    logger.info("✅ Banco de dados inicializado!")
    
    # Inicia bot do Telegram em background
    logger.info("🤖 Iniciando bot do Telegram...")
    bot_task = asyncio.create_task(asyncio.to_thread(start_bot))
    
    logger.info("✅ Sistema inicializado com sucesso!")
    
    yield
    
    # Shutdown
    logger.info("🛑 Encerrando sistema...")
    bot_task.cancel()
    logger.info("👋 Sistema encerrado!")

# Criar aplicação FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description="Sistema inteligente de agendamento com IA para clínicas, salões e barbearias",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "app": settings.APP_NAME,
        "status": "running",
        "version": "1.0.0",
        "message": "Sistema de Agendamento Inteligente operacional! 🚀"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": "2026-01-10"}

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"🌟 Iniciando {settings.APP_NAME}...")
    logger.info(f"🔧 Modo Debug: {settings.DEBUG}")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )