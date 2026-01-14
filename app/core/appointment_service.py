from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict
from app.db.models import (
    Appointment, AppointmentStatus, ClientProfile, 
    ProfessionalProfile, Service, ReliabilityLevel
)
from app.config import settings

class AppointmentService:
    """Serviço para gerenciamento de agendamentos"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_appointment(
        self,
        client_id: int,
        professional_id: int,
        service_id: int,
        scheduled_date: datetime,
        notes: Optional[str] = None
    ) -> Appointment:
        """Cria novo agendamento"""
        
        # Verifica se horário está disponível
        if not self.is_time_slot_available(professional_id, scheduled_date):
            raise ValueError("Horário não disponível")
        
        # Verifica confiabilidade do cliente para horários de pico
        client = self.db.query(ClientProfile).filter_by(id=client_id).first()
        if self._is_peak_time(scheduled_date) and client.reliability_level == ReliabilityLevel.LOW:
            raise ValueError("Cliente com baixa confiabilidade não pode agendar em horários de pico")
        
        appointment = Appointment(
            client_id=client_id,
            professional_id=professional_id,
            service_id=service_id,
            scheduled_date=scheduled_date,
            notes=notes,
            status=AppointmentStatus.SCHEDULED
        )
        
        self.db.add(appointment)
        
        # Atualiza contadores do cliente
        client.total_appointments += 1
        
        self.db.commit()
        self.db.refresh(appointment)
        
        return appointment
    
    def cancel_appointment(
        self,
        appointment_id: int,
        reason: str,
        cancelled_by_client: bool = True
    ) -> Appointment:
        """Cancela agendamento"""
        
        appointment = self.db.query(Appointment).filter_by(id=appointment_id).first()
        if not appointment:
            raise ValueError("Agendamento não encontrado")
        
        if appointment.status == AppointmentStatus.CANCELLED:
            raise ValueError("Agendamento já cancelado")
        
        # Verifica se é cancelamento em cima da hora
        hours_until = (appointment.scheduled_date - datetime.now()).total_seconds() / 3600
        
        if cancelled_by_client and hours_until < settings.CANCELLATION_LIMIT_HOURS:
            # Penaliza cliente por cancelamento tardio
            client = appointment.client
            client.late_cancellation_count += 1
            self._update_reliability(client)
        
        appointment.status = AppointmentStatus.CANCELLED
        appointment.cancellation_reason = reason
        appointment.cancelled_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(appointment)
        
        return appointment
    
    def mark_no_show(self, appointment_id: int) -> Appointment:
        """Marca cliente como faltoso"""
        
        appointment = self.db.query(Appointment).filter_by(id=appointment_id).first()
        if not appointment:
            raise ValueError("Agendamento não encontrado")
        
        appointment.status = AppointmentStatus.NO_SHOW
        
        # Penaliza cliente
        client = appointment.client
        client.no_show_count += 1
        self._update_reliability(client)
        
        self.db.commit()
        self.db.refresh(appointment)
        
        return appointment
    
    def complete_appointment(self, appointment_id: int) -> Appointment:
        """Marca agendamento como completado"""
        
        appointment = self.db.query(Appointment).filter_by(id=appointment_id).first()
        if not appointment:
            raise ValueError("Agendamento não encontrado")
        
        appointment.status = AppointmentStatus.COMPLETED
        appointment.completed_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(appointment)
        
        return appointment
    
    def get_available_slots(
        self,
        professional_id: int,
        date: datetime,
        service_id: int
    ) -> List[Dict]:
        """Retorna horários disponíveis para um profissional em uma data"""
        
        service = self.db.query(Service).filter_by(id=service_id).first()
        if not service:
            return []
        
        # Busca agendamentos existentes do profissional nesta data
        start_of_day = date.replace(hour=0, minute=0, second=0)
        end_of_day = date.replace(hour=23, minute=59, second=59)
        
        existing = self.db.query(Appointment).filter(
            and_(
                Appointment.professional_id == professional_id,
                Appointment.scheduled_date >= start_of_day,
                Appointment.scheduled_date <= end_of_day,
                Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED])
            )
        ).all()
        
        # Gera slots possíveis
        business_start = datetime.strptime(settings.BUSINESS_HOURS_START, "%H:%M")
        business_end = datetime.strptime(settings.BUSINESS_HOURS_END, "%H:%M")
        
        available_slots = []
        current_time = date.replace(
            hour=business_start.hour,
            minute=business_start.minute,
            second=0
        )
        
        while current_time.hour < business_end.hour or \
              (current_time.hour == business_end.hour and current_time.minute < business_end.minute):
            
            # Verifica se slot está livre
            is_available = True
            for apt in existing:
                apt_service = apt.service
                apt_end = apt.scheduled_date + timedelta(minutes=apt_service.duration_minutes)
                service_end = current_time + timedelta(minutes=service.duration_minutes)
                
                # Verifica sobreposição
                if not (service_end <= apt.scheduled_date or current_time >= apt_end):
                    is_available = False
                    break
            
            # Não permite agendamento no passado
            if current_time <= datetime.now():
                is_available = False
            
            if is_available:
                available_slots.append({
                    "time": current_time.strftime("%H:%M"),
                    "datetime": current_time,
                    "is_peak": self._is_peak_time(current_time)
                })
            
            # Próximo slot (incrementa em 30 minutos)
            current_time += timedelta(minutes=30)
        
        return available_slots
    
    def is_time_slot_available(
        self,
        professional_id: int,
        scheduled_date: datetime,
        service_duration: int = 60
    ) -> bool:
        """Verifica se horário está disponível"""
        
        end_time = scheduled_date + timedelta(minutes=service_duration)
        
        conflicts = self.db.query(Appointment).filter(
            and_(
                Appointment.professional_id == professional_id,
                Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED]),
                or_(
                    and_(
                        Appointment.scheduled_date <= scheduled_date,
                        Appointment.scheduled_date + timedelta(minutes=60) > scheduled_date
                    ),
                    and_(
                        Appointment.scheduled_date < end_time,
                        Appointment.scheduled_date >= scheduled_date
                    )
                )
            )
        ).count()
        
        return conflicts == 0
    
    def get_client_appointments(
        self,
        client_id: int,
        include_past: bool = False
    ) -> List[Appointment]:
        """Retorna agendamentos de um cliente"""
        
        query = self.db.query(Appointment).filter_by(client_id=client_id)
        
        if not include_past:
            query = query.filter(Appointment.scheduled_date >= datetime.now())
        
        return query.order_by(Appointment.scheduled_date).all()
    
    def get_professional_appointments(
        self,
        professional_id: int,
        date: Optional[datetime] = None
    ) -> List[Appointment]:
        """Retorna agendamentos de um profissional"""
        
        query = self.db.query(Appointment).filter_by(professional_id=professional_id)
        
        if date:
            start_of_day = date.replace(hour=0, minute=0, second=0)
            end_of_day = date.replace(hour=23, minute=59, second=59)
            query = query.filter(
                and_(
                    Appointment.scheduled_date >= start_of_day,
                    Appointment.scheduled_date <= end_of_day
                )
            )
        else:
            query = query.filter(Appointment.scheduled_date >= datetime.now())
        
        return query.order_by(Appointment.scheduled_date).all()
    
    def _update_reliability(self, client: ClientProfile):
        """Atualiza nível de confiabilidade do cliente"""
        
        total_issues = client.no_show_count + client.late_cancellation_count
        
        if total_issues == 0:
            client.reliability_level = ReliabilityLevel.EXCELLENT
        elif total_issues <= 2:
            client.reliability_level = ReliabilityLevel.GOOD
        elif total_issues <= 4:
            client.reliability_level = ReliabilityLevel.MODERATE
        else:
            client.reliability_level = ReliabilityLevel.LOW
    
    def _is_peak_time(self, dt: datetime) -> bool:
        """Verifica se é horário de pico"""
        # Considera horários de pico: 18h-20h nos dias de semana
        return dt.weekday() < 5 and 18 <= dt.hour < 20
    
    def suggest_alternatives(
        self,
        professional_id: int,
        preferred_date: datetime,
        service_id: int
    ) -> List[Dict]:
        """Sugere horários alternativos próximos à data preferida"""
        
        alternatives = []
        
        # Tenta encontrar horários nos próximos 7 dias
        for days_offset in range(7):
            check_date = preferred_date + timedelta(days=days_offset)
            slots = self.get_available_slots(professional_id, check_date, service_id)
            
            if slots:
                alternatives.append({
                    "date": check_date,
                    "slots": slots[:5]  # Máximo 5 sugestões por dia
                })
            
            if len(alternatives) >= 3:  # Máximo 3 dias alternativos
                break
        
        return alternatives