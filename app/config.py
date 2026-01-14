import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./scheduling.db")
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    
    # Anthropic Claude API
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    CLAUDE_MODEL: str = "claude-sonnet-4-20250514"
    
    # App Settings
    APP_NAME: str = "Sistema de Agendamento Inteligente"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Business Rules
    CANCELLATION_LIMIT_HOURS: int = 4  # Horas mínimas para cancelamento
    MAX_NO_SHOW_COUNT: int = 3  # Máximo de faltas antes de restrições
    ALERT_BEFORE_APPOINTMENT_HOURS: int = 24  # Alerta 24h antes
    REMINDER_BEFORE_APPOINTMENT_MINUTES: int = 60  # Lembrete 1h antes
    
    # Horários de funcionamento
    BUSINESS_HOURS_START: str = "08:00"
    BUSINESS_HOURS_END: str = "20:00"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()