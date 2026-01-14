import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)
from app.config import settings
from app.telegram.handlers import TelegramHandlers

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class SchedulingBot:
    """Bot principal de agendamento"""
    
    def __init__(self):
        self.application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
        self.handlers = TelegramHandlers()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Configura todos os handlers do bot"""
        
        # Comandos básicos
        self.application.add_handler(CommandHandler("start", self.handlers.start))
        self.application.add_handler(CommandHandler("menu", self.handlers.show_menu))
        self.application.add_handler(CommandHandler("help", self.handlers.help_command))
        self.application.add_handler(CommandHandler("cancelar", self.handlers.cancel_command))
        
        # Callbacks de botões inline
        self.application.add_handler(CallbackQueryHandler(
            self.handlers.handle_callback
        ))
        
        # Mensagens de texto (conversação com IA)
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.handlers.handle_message
        ))
        
        # Handler de erros
        self.application.add_error_handler(self.error_handler)
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler global de erros"""
        logger.error(f"Erro ao processar update: {context.error}")
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Desculpe, ocorreu um erro inesperado. "
                "Por favor, tente novamente ou entre em contato com o suporte."
            )
    
    def run(self):
        """Inicia o bot"""
        logger.info("🤖 Bot iniciado! Aguardando mensagens...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

# Função para criar e executar o bot
def start_bot():
    bot = SchedulingBot()
    bot.run()

if __name__ == "__main__":
    start_bot()