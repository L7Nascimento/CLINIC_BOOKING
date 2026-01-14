"""
API REST para gerenciamento de agendamentos
Endpoints para integração web/mobile futura
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from app.db.session import get_db
from app.db.models import Appointment, AppointmentStatus, User, UserRole
from app.core.appointment_service import AppointmentService
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/appointments", tags=["Appointments"])

# Schemas Pydantic para request/response

class AppointmentCreate(BaseModel):
    client_id: int
    professional_id: int
    service_id: int
    scheduled_date: datetime
    notes: str | None = None

class AppointmentResponse(BaseModel):
    id: int
    client_name: str
    professional_name: str
    service_name: str
    scheduled_date: datetime
    status: str
    price: float
    
    class Config:
        from_attributes = True

class AvailableSlot(BaseModel):
    time: str
    datetime: datetime
    is_peak: bool

class AppointmentCancel(BaseModel):
    reason: str

# Endpoints

@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    appointment_data: AppointmentCreate,
    db: Session = Depends(get_db)
):
    """
    Cria novo agendamento
    
    - **client_id**: ID do cliente
    - **professional_id**: ID do profissional
    - **service_id**: ID do serviço
    - **scheduled_date**: Data e hora do agendamento
    - **notes**: Observações (opcional)
    """
    service = AppointmentService(db)
    
    try:
        appointment = service.create_appointment(
            client_id=appointment_data.client_id,
            professional_id=appointment_data.professional_id,
            service_id=appointment_data.service_id,
            scheduled_date=appointment_data.scheduled_date,
            notes=appointment_data.notes
        )
        
        return AppointmentResponse(
            id=appointment.id,
            client_name=appointment.client.user.name,
            professional_name=appointment.professional.user.name,
            service_name=appointment.service.name,
            scheduled_date=appointment.scheduled_date,
            status=appointment.status.value,
            price=appointment.service.price
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/available-slots", response_model=List[AvailableSlot])
async def get_available_slots(
    professional_id: int,
    date: str,  # YYYY-MM-DD
    service_id: int,
    db: Session = Depends(get_db)
):
    """
    Retorna horários disponíveis para agendamento
    
    - **professional_id**: ID do profissional
    - **date**: Data desejada (YYYY-MM-DD)
    - **service_id**: ID do serviço
    """
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de data inválido. Use YYYY-MM-DD")
    
    service = AppointmentService(db)
    slots = service.get_available_slots(professional_id, date_obj, service_id)
    
    return slots

@router.get("/client/{client_id}", response_model=List[AppointmentResponse])
async def get_client_appointments(
    client_id: int,
    include_past: bool = False,
    db: Session = Depends(get_db)
):
    """
    Lista agendamentos de um cliente
    
    - **client_id**: ID do cliente
    - **include_past**: Incluir agendamentos passados (default: False)
    """
    service = AppointmentService(db)
    appointments = service.get_client_appointments(client_id, include_past)
    
    return [
        AppointmentResponse(
            id=apt.id,
            client_name=apt.client.user.name,
            professional_name=apt.professional.user.name,
            service_name=apt.service.name,
            scheduled_date=apt.scheduled_date,
            status=apt.status.value,
            price=apt.service.price
        )
        for apt in appointments
    ]

@router.get("/professional/{professional_id}", response_model=List[AppointmentResponse])
async def get_professional_appointments(
    professional_id: int,
    date: str | None = None,  # YYYY-MM-DD
    db: Session = Depends(get_db)
):
    """
    Lista agendamentos de um profissional
    
    - **professional_id**: ID do profissional
    - **date**: Data específica (opcional, default: todos futuros)
    """
    date_obj = None
    if date:
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de data inválido")
    
    service = AppointmentService(db)
    appointments = service.get_professional_appointments(professional_id, date_obj)
    
    return [
        AppointmentResponse(
            id=apt.id,
            client_name=apt.client.user.name,
            professional_name=apt.professional.user.name,
            service_name=apt.service.name,
            scheduled_date=apt.scheduled_date,
            status=apt.status.value,
            price=apt.service.price
        )
        for apt in appointments
    ]

@router.patch("/{appointment_id}/cancel", response_model=AppointmentResponse)
async def cancel_appointment(
    appointment_id: int,
    cancel_data: AppointmentCancel,
    db: Session = Depends(get_db)
):
    """
    Cancela um agendamento
    
    - **appointment_id**: ID do agendamento
    - **reason**: Motivo do cancelamento
    """
    service = AppointmentService(db)
    
    try:
        appointment = service.cancel_appointment(
            appointment_id=appointment_id,
            reason=cancel_data.reason,
            cancelled_by_client=True
        )
        
        return AppointmentResponse(
            id=appointment.id,
            client_name=appointment.client.user.name,
            professional_name=appointment.professional.user.name,
            service_name=appointment.service.name,
            scheduled_date=appointment.scheduled_date,
            status=appointment.status.value,
            price=appointment.service.price
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{appointment_id}/complete", response_model=AppointmentResponse)
async def complete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db)
):
    """
    Marca agendamento como completado
    
    - **appointment_id**: ID do agendamento
    """
    service = AppointmentService(db)
    
    try:
        appointment = service.complete_appointment(appointment_id)
        
        return AppointmentResponse(
            id=appointment.id,
            client_name=appointment.client.user.name,
            professional_name=appointment.professional.user.name,
            service_name=appointment.service.name,
            scheduled_date=appointment.scheduled_date,
            status=appointment.status.value,
            price=appointment.service.price
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{appointment_id}/no-show", response_model=AppointmentResponse)
async def mark_no_show(
    appointment_id: int,
    db: Session = Depends(get_db)
):
    """
    Marca cliente como faltoso (no-show)
    
    - **appointment_id**: ID do agendamento
    
    Isso penaliza o nível de confiabilidade do cliente.
    """
    service = AppointmentService(db)
    
    try:
        appointment = service.mark_no_show(appointment_id)
        
        return AppointmentResponse(
            id=appointment.id,
            client_name=appointment.client.user.name,
            professional_name=appointment.professional.user.name,
            service_name=appointment.service.name,
            scheduled_date=appointment.scheduled_date,
            status=appointment.status.value,
            price=appointment.service.price
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/statistics/daily")
async def get_daily_statistics(
    date: str | None = None,  # YYYY-MM-DD
    db: Session = Depends(get_db)
):
    """
    Retorna estatísticas do dia
    
    - **date**: Data (opcional, default: hoje)
    """
    if date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de data inválido")
    else:
        target_date = datetime.now()
    
    start_of_day = target_date.replace(hour=0, minute=0, second=0)
    end_of_day = target_date.replace(hour=23, minute=59, second=59)
    
    # Busca agendamentos do dia
    appointments = db.query(Appointment).filter(
        Appointment.scheduled_date >= start_of_day,
        Appointment.scheduled_date <= end_of_day
    ).all()
    
    total = len(appointments)
    completed = len([a for a in appointments if a.status == AppointmentStatus.COMPLETED])
    cancelled = len([a for a in appointments if a.status == AppointmentStatus.CANCELLED])
    no_shows = len([a for a in appointments if a.status == AppointmentStatus.NO_SHOW])
    scheduled = len([a for a in appointments if a.status == AppointmentStatus.SCHEDULED])
    
    revenue = sum([
        a.service.price for a in appointments 
        if a.status == AppointmentStatus.COMPLETED
    ])
    
    return {
        "date": target_date.strftime("%Y-%m-%d"),
        "total_appointments": total,
        "completed": completed,
        "cancelled": cancelled,
        "no_shows": no_shows,
        "scheduled": scheduled,
        "revenue": revenue,
        "completion_rate": (completed / total * 100) if total > 0 else 0
    }