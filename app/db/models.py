from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class UserRole(enum.Enum):
    CLIENT = "client"
    PROFESSIONAL = "professional"
    ADMIN = "admin"

class AppointmentStatus(enum.Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class ReliabilityLevel(enum.Enum):
    EXCELLENT = "excellent"  # 0 faltas
    GOOD = "good"  # 1-2 faltas
    MODERATE = "moderate"  # 3-4 faltas
    LOW = "low"  # 5+ faltas

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String)
    email = Column(String)
    role = Column(Enum(UserRole), default=UserRole.CLIENT)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    client_profile = relationship("ClientProfile", back_populates="user", uselist=False)
    professional_profile = relationship("ProfessionalProfile", back_populates="user", uselist=False)

class ClientProfile(Base):
    __tablename__ = "client_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    # Métricas de confiabilidade
    no_show_count = Column(Integer, default=0)
    late_cancellation_count = Column(Integer, default=0)
    total_appointments = Column(Integer, default=0)
    reliability_level = Column(Enum(ReliabilityLevel), default=ReliabilityLevel.EXCELLENT)
    
    # Preferências
    preferred_professional_id = Column(Integer, ForeignKey("professional_profiles.id"), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relacionamentos
    user = relationship("User", back_populates="client_profile")
    appointments = relationship("Appointment", back_populates="client")
    messages = relationship("Message", back_populates="client")

class ProfessionalProfile(Base):
    __tablename__ = "professional_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    specialty = Column(String)
    commission_percentage = Column(Float, default=50.0)  # % do serviço
    is_available = Column(Boolean, default=True)
    
    # Relacionamentos
    user = relationship("User", back_populates="professional_profile")
    appointments = relationship("Appointment", back_populates="professional")
    services = relationship("Service", secondary="professional_services")
    schedules = relationship("ProfessionalSchedule", back_populates="professional")

class Service(Base):
    __tablename__ = "services"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    duration_minutes = Column(Integer, nullable=False)  # Duração em minutos
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    appointments = relationship("Appointment", back_populates="service")

class ProfessionalService(Base):
    __tablename__ = "professional_services"
    
    professional_id = Column(Integer, ForeignKey("professional_profiles.id"), primary_key=True)
    service_id = Column(Integer, ForeignKey("services.id"), primary_key=True)

class Appointment(Base):
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("client_profiles.id"), nullable=False)
    professional_id = Column(Integer, ForeignKey("professional_profiles.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    
    scheduled_date = Column(DateTime, nullable=False, index=True)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.SCHEDULED)
    
    # Detalhes
    notes = Column(Text)
    cancellation_reason = Column(Text)
    cancelled_at = Column(DateTime)
    confirmed_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Alertas enviados
    alert_24h_sent = Column(Boolean, default=False)
    alert_1h_sent = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    client = relationship("ClientProfile", back_populates="appointments")
    professional = relationship("ProfessionalProfile", back_populates="appointments")
    service = relationship("Service", back_populates="appointments")

class ProfessionalSchedule(Base):
    __tablename__ = "professional_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    professional_id = Column(Integer, ForeignKey("professional_profiles.id"))
    
    day_of_week = Column(Integer)  # 0-6 (Segunda a Domingo)
    start_time = Column(String)  # HH:MM
    end_time = Column(String)  # HH:MM
    is_active = Column(Boolean, default=True)
    
    professional = relationship("ProfessionalProfile", back_populates="schedules")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("client_profiles.id"))
    subject = Column(String)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    response = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    client = relationship("ClientProfile", back_populates="messages")

class FinancialRecord(Base):
    __tablename__ = "financial_records"
    
    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"))
    professional_id = Column(Integer, ForeignKey("professional_profiles.id"))
    
    service_price = Column(Float, nullable=False)
    professional_commission = Column(Float, nullable=False)
    business_revenue = Column(Float, nullable=False)
    
    date = Column(DateTime, default=datetime.utcnow, index=True)
    notes = Column(Text)