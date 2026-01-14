import logging
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models import User, UserRole, ClientProfile, ProfessionalProfile, Service
from app.telegram.keyboards import Keyboards
from app.core.ai_service import ai_service
from app.core.appointment_service import AppointmentService

logger = logging.getLogger(__name__)

class TelegramHandlers:
    """Handlers para mensagens e callbacks do Telegram"""
    
    def __init__(self):
        self.keyboards = Keyboards()
        self.user_states = {}  # Armazena estado da conversa de cada usuário
    
    def get_db(self) -> Session:
        """Retorna sessão do banco de dados"""
        return SessionLocal()
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para comando /start"""
        user = update.effective_user
        db = self.get_db()
        
        try:
            # Busca ou cria usuário
            db_user = db.query(User).filter_by(telegram_id=str(user.id)).first()
            
            if not db_user:
                # Novo usuário - processo de cadastro
                await update.message.reply_text(
                    f"👋 Olá! Seja bem-vindo(a) ao nosso sistema de agendamento!\n\n"
                    f"Vejo que é sua primeira vez aqui. "
                    f"Vou precisar de algumas informações para criar seu cadastro.\n\n"
                    f"Por favor, me informe seu nome completo:"
                )
                
                # Define estado para cadastro
                self.user_states[user.id] = {"state": "awaiting_name"}
            else:
                # Usuário existente
                await self._show_welcome_back(update, db_user, db)
        
        finally:
            db.close()
    
    async def _show_welcome_back(self, update: Update, db_user: User, db: Session):
        """Mostra boas-vindas para usuário existente"""
        
        # Busca próximos agendamentos se for cliente
        next_appointments_text = ""
        if db_user.role == UserRole.CLIENT and db_user.client_profile:
            apt_service = AppointmentService(db)
            appointments = apt_service.get_client_appointments(
                db_user.client_profile.id,
                include_past=False
            )
            
            if appointments:
                next_apt = appointments[0]
                next_appointments_text = (
                    f"\n\n📅 Seu próximo agendamento:\n"
                    f"• {next_apt.service.name}\n"
                    f"• {next_apt.scheduled_date.strftime('%d/%m/%Y às %H:%M')}\n"
                    f"• Com: {next_apt.professional.user.name}"
                )
        
        welcome_message = (
            f"👋 Olá, {db_user.name}!\n"
            f"É um prazer ter você de volta!{next_appointments_text}\n\n"
            f"Como posso ajudá-lo(a) hoje?"
        )
        
        await update.message.reply_text(
            welcome_message,
            reply_markup=self.keyboards.main_menu(db_user.role.value)
        )
    
    async def show_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mostra menu principal"""
        user = update.effective_user
        db = self.get_db()
        
        try:
            db_user = db.query(User).filter_by(telegram_id=str(user.id)).first()
            
            if not db_user:
                await update.message.reply_text(
                    "❌ Você precisa se cadastrar primeiro. Use /start"
                )
                return
            
            await update.message.reply_text(
                "📋 Menu Principal:",
                reply_markup=self.keyboards.main_menu(db_user.role.value)
            )
        finally:
            db.close()
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para comando /help"""
        help_text = (
            "🤖 *Comandos Disponíveis:*\n\n"
            "/start - Iniciar ou retornar ao menu\n"
            "/menu - Exibir menu principal\n"
            "/cancelar - Cancelar operação atual\n"
            "/help - Exibir esta ajuda\n\n"
            "💬 *Você também pode conversar comigo naturalmente!*\n"
            "Experimente dizer:\n"
            "• \"Quero agendar um corte de cabelo\"\n"
            "• \"Quais serviços vocês oferecem?\"\n"
            "• \"Preciso cancelar meu agendamento\"\n"
            "• \"Qual horário disponível amanhã?\"\n\n"
            "Estou aqui para ajudar! 😊"
        )
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def cancel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancela operação atual"""
        user = update.effective_user
        
        if user.id in self.user_states:
            del self.user_states[user.id]
        
        await update.message.reply_text(
            "✅ Operação cancelada. Use /menu para voltar ao menu principal."
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para mensagens de texto (conversação com IA)"""
        user = update.effective_user
        message_text = update.message.text
        db = self.get_db()
        
        try:
            # Verifica se usuário existe
            db_user = db.query(User).filter_by(telegram_id=str(user.id)).first()
            
            if not db_user:
                await update.message.reply_text(
                    "❌ Você precisa se cadastrar primeiro. Use /start"
                )
                return
            
            # Verifica se está em processo de cadastro ou outra operação
            if user.id in self.user_states:
                await self._handle_state_based_message(update, db_user, db)
                return
            
            # Processamento normal com IA
            await self._process_with_ai(update, db_user, db, message_text)
        
        finally:
            db.close()
    
    async def _handle_state_based_message(self, update: Update, db_user: User, db: Session):
        """Processa mensagem baseada no estado atual do usuário"""
        user = update.effective_user
        state_data = self.user_states.get(user.id, {})
        current_state = state_data.get("state")
        
        if current_state == "awaiting_name":
            # Cadastrando nome
            name = update.message.text.strip()
            
            # Cria usuário
            new_user = User(
                telegram_id=str(user.id),
                name=name,
                role=UserRole.CLIENT
            )
            db.add(new_user)
            db.flush()
            
            # Cria perfil de cliente
            client_profile = ClientProfile(user_id=new_user.id)
            db.add(client_profile)
            db.commit()
            
            await update.message.reply_text(
                f"✅ Perfeito, {name}! Cadastro concluído com sucesso!\n\n"
                f"Agora você já pode usar todos os recursos do sistema. 🎉"
            )
            
            # Remove estado
            del self.user_states[user.id]
            
            # Mostra menu
            await update.message.reply_text(
                "📋 Veja o que você pode fazer:",
                reply_markup=self.keyboards.main_menu("client")
            )
        
        elif current_state == "awaiting_message_to_management":
            # Enviando mensagem para gerência
            from app.db.models import Message
            
            message = Message(
                client_id=db_user.client_profile.id,
                subject="Mensagem do cliente",
                content=update.message.text
            )
            db.add(message)
            db.commit()
            
            await update.message.reply_text(
                "✅ Mensagem enviada para a gerência com sucesso!\n"
                "Retornaremos em breve. Obrigado!"
            )
            
            del self.user_states[user.id]
    
    async def _process_with_ai(self, update: Update, db_user: User, db: Session, message: str):
        """Processa mensagem usando IA Claude"""
        
        # Prepara contexto
        context = {
            "user_name": db_user.name,
            "user_role": db_user.role.value
        }
        
        # Busca serviços disponíveis
        services = db.query(Service).filter_by(is_active=True).all()
        context["available_services"] = [
            {
                "name": s.name,
                "price": s.price,
                "duration_minutes": s.duration_minutes
            }
            for s in services
        ]
        
        # Se for cliente, adiciona info de agendamentos
        if db_user.client_profile:
            apt_service = AppointmentService(db)
            appointments = apt_service.get_client_appointments(
                db_user.client_profile.id,
                include_past=False
            )
            context["user_appointments"] = len(appointments)
            context["reliability_level"] = db_user.client_profile.reliability_level.value
        
        # Envia "digitando..."
        await update.message.chat.send_action("typing")
        
        # Processa com IA
        response = await ai_service.chat(message, context=context)
        
        # Analisa intenção para ações específicas
        intent_data = await ai_service.analyze_appointment_request(message)
        
        # Responde
        await update.message.reply_text(response)
        
        # Se detectou intenção de agendamento, oferece menu
        if intent_data.get("intent") == "schedule":
            await update.message.reply_text(
                "📅 Gostaria de fazer o agendamento agora?",
                reply_markup=self.keyboards.main_menu(db_user.role.value)
            )
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para callbacks de botões inline"""
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        db = self.get_db()
        
        try:
            user = query.from_user
            db_user = db.query(User).filter_by(telegram_id=str(user.id)).first()
            
            if not db_user:
                await query.message.reply_text("❌ Erro: usuário não encontrado")
                return
            
            # Roteamento de callbacks
            if callback_data == "back_to_menu":
                await self._handle_back_to_menu(query, db_user)
            
            elif callback_data == "new_appointment":
                await self._handle_new_appointment(query, db)
            
            elif callback_data == "my_appointments":
                await self._handle_my_appointments(query, db_user, db)
            
            elif callback_data == "view_services":
                await self._handle_view_services(query, db)
            
            elif callback_data == "contact_management":
                await self._handle_contact_management(query, user)
            
            # Adicione mais handlers conforme necessário...
            elif callback_data == "view_professionals":
                await self._handle_view_professionals(query, db)
            elif callback_data == "my_profile":
                await self._handle_my_profile(query, db_user, db)
            # Callback para seleção de serviço
            elif callback_data.startswith("service_"):
                service_id = int(callback_data.split("_")[1])
                await self._handle_service_selected(query, service_id, db)
            elif callback_data.startswith("professional_"):
                professional_id = int(callback_data.split("_")[1])
                await self._handle_professional_selected(query, professional_id, db)
            elif callback_data.startswith("date_"):
                date_str = callback_data.split("_")[1]
                await self._handle_date_selected(query, date_str, db)
            
        finally:
            db.close()
    
    async def _handle_back_to_menu(self, query, db_user):
        """Volta ao menu principal"""
        await query.edit_message_text(
            "📋 Menu Principal:",
            reply_markup=self.keyboards.main_menu(db_user.role.value)
        )
    
    async def _handle_new_appointment(self, query, db: Session):
        """Inicia processo de novo agendamento"""
        services = db.query(Service).filter_by(is_active=True).all()
        
        services_data = [
            {"id": s.id, "name": s.name, "price": s.price}
            for s in services
        ]
        
        await query.edit_message_text(
            "💼 Escolha o serviço desejado:",
            reply_markup=self.keyboards.service_selection(services_data)
        )
    
    async def _handle_my_appointments(self, query, db_user, db: Session):
        """Mostra agendamentos do cliente"""
        if not db_user.client_profile:
            await query.edit_message_text("❌ Erro: perfil de cliente não encontrado")
            return
        
        apt_service = AppointmentService(db)
        appointments = apt_service.get_client_appointments(
            db_user.client_profile.id,
            include_past=False
        )
        
        if not appointments:
            await query.edit_message_text(
                "📅 Você não possui agendamentos futuros.\n\n"
                "Gostaria de fazer um novo agendamento?",
                reply_markup=self.keyboards.main_menu("client")
            )
            return
        
        message = "📅 *Seus Agendamentos:*\n\n"
        
        for apt in appointments:
            status_emoji = {
                "scheduled": "🕐",
                "confirmed": "✅",
                "completed": "✔️",
                "cancelled": "❌"
            }.get(apt.status.value, "❓")
            
            message += (
                f"{status_emoji} *{apt.service.name}*\n"
                f"📅 {apt.scheduled_date.strftime('%d/%m/%Y às %H:%M')}\n"
                f"👤 Com: {apt.professional.user.name}\n"
                f"💰 R$ {apt.service.price:.2f}\n\n"
            )
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=self.keyboards.back_button()
        )
    
    async def _handle_view_services(self, query, db: Session):
        """Mostra lista de serviços"""
        services = db.query(Service).filter_by(is_active=True).all()
        
        message = "💼 *Nossos Serviços:*\n\n"
        
        for service in services:
            message += (
                f"✂️ *{service.name}*\n"
                f"💰 R$ {service.price:.2f}\n"
                f"⏱️ Duração: {service.duration_minutes} minutos\n"
            )
            if service.description:
                message += f"📝 {service.description}\n"
            message += "\n"
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=self.keyboards.back_button()
        )
    
    async def _handle_contact_management(self, query, user):
        """Inicia processo de envio de mensagem à gerência"""
        self.user_states[user.id] = {"state": "awaiting_message_to_management"}
        
        await query.edit_message_text(
            "💬 *Falar com a Gerência*\n\n"
            "Por favor, digite sua mensagem e enviarei para nossa equipe.\n"
            "Retornaremos o mais breve possível!",
            parse_mode='Markdown'
        )
    async def _handle_view_professionals(self, query, db: Session):

        """Mostra lista de profissionais"""
        professionals = db.query(ProfessionalProfile).filter_by(is_available=True).all()
        
        if not professionals:
            await query.edit_message_text(
                "❌ Nenhum profissional disponível no momento.",
                reply_markup=self.keyboards.back_button()
            )
            return
        
        message = "👨‍💼 *Nossos Profissionais:*\n\n"
        
        for prof in professionals:
            status = "✅ Disponível" if prof.is_available else "🔴 Indisponível"
            message += (
                f"👤 *{prof.user.name}*\n"
                f"💼 {prof.specialty}\n"
                f"📊 {status}\n\n"
            )
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=self.keyboards.back_button()
        )
    async def _handle_my_profile(self, query, db_user, db: Session):
    
        """Mostra perfil do usuário"""
        if not db_user.client_profile:
            await query.edit_message_text("❌ Perfil não encontrado")
            return
        
        profile = db_user.client_profile
        
        # Calcula taxa de comparecimento
        total = profile.total_appointments
        issues = profile.no_show_count + profile.late_cancellation_count
        reliability_emoji = {
            "excellent": "🌟",
            "good": "✅",
            "moderate": "⚠️",
            "low": "❌"
        }.get(profile.reliability_level.value, "❓")
        
        message = (
            f"👤 *Seu Perfil*\n\n"
            f"📝 Nome: {db_user.name}\n"
            f"📊 Confiabilidade: {reliability_emoji} {profile.reliability_level.value.title()}\n"
            f"📅 Total de agendamentos: {total}\n"
            f"❌ Faltas: {profile.no_show_count}\n"
            f"⏰ Cancelamentos tardios: {profile.late_cancellation_count}\n\n"
        )
        
        if profile.reliability_level.value == "low":
            message += "⚠️ *Atenção:* Devido ao histórico, você não pode agendar em horários de pico.\n"
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=self.keyboards.back_button()
        )
    async def _handle_service_selected(self, query, service_id: int, db: Session):
        """Processa seleção de serviço e mostra profissionais"""
        # Busca profissionais disponíveis para este serviço
        professionals = db.query(ProfessionalProfile).filter(
            ProfessionalProfile.is_available == True
        ).all()
        
        # Filtra profissionais que oferecem este serviço
        available_profs = []
        for prof in professionals:
            if any(s.id == service_id for s in prof.services):
                available_profs.append({
                    "id": prof.id,
                    "name": prof.user.name,
                    "specialty": prof.specialty,
                    "is_available": prof.is_available
                })
        
        if not available_profs:
            await query.edit_message_text(
                "❌ Nenhum profissional disponível para este serviço no momento.\n\n"
                "Por favor, escolha outro serviço ou tente mais tarde.",
                reply_markup=self.keyboards.back_button()
            )
            return
        
        # Salva serviço selecionado no estado do usuário
        user_id = query.from_user.id
        self.user_states[user_id] = {
            "state": "selecting_professional",
            "service_id": service_id
        }
        
        await query.edit_message_text(
            "👨‍💼 Escolha o profissional:",
            reply_markup=self.keyboards.professional_selection(available_profs)
        )
    async def _handle_professional_selected(self, query, professional_id: int, db: Session):
        """Processa seleção de profissional e mostra datas disponíveis"""
        user_id = query.from_user.id
        
        # Recupera dados do estado
        state = self.user_states.get(user_id, {})
        service_id = state.get("service_id")
        
        if not service_id:
            await query.edit_message_text(
                "❌ Erro: serviço não encontrado. Por favor, comece novamente.",
                reply_markup=self.keyboards.back_button()
            )
            return
        
        # Busca informações do serviço e profissional
        service = db.query(Service).filter_by(id=service_id).first()
        professional = db.query(ProfessionalProfile).filter_by(id=professional_id).first()
        
        if not service or not professional:
            await query.edit_message_text(
                "❌ Erro ao carregar informações. Tente novamente.",
                reply_markup=self.keyboards.back_button()
            )
            return
        
        # Atualiza estado
        self.user_states[user_id] = {
            "state": "selecting_date",
            "service_id": service_id,
            "professional_id": professional_id
        }
        
        # Mostra seleção de data
        message = (
            f"✅ Você selecionou:\n\n"
            f"💼 Serviço: {service.name}\n"
            f"👤 Profissional: {professional.user.name}\n"
            f"💰 Valor: R$ {service.price:.2f}\n"
            f"⏱️ Duração: {service.duration_minutes} minutos\n\n"
            f"📅 Escolha uma data:"
        )
        
        await query.edit_message_text(
            message,
            reply_markup=self.keyboards.date_selection()
        )
    async def _handle_date_selected(self, query, date_str: str, db: Session):
        """Processa seleção de data e mostra horários disponíveis"""
        from datetime import datetime
    
        user_id = query.from_user.id
    
        # Recupera dados do estado
        state = self.user_states.get(user_id, {})
        service_id = state.get("service_id")
        professional_id = state.get("professional_id")
    
        if not service_id or not professional_id:
            await query.edit_message_text(
            "❌ Erro: dados não encontrados. Por favor, comece novamente.",
            reply_markup=self.keyboards.back_button()
        )
        return
    
        # Converte string de data para datetime
        try:
            selected_date = datetime.strptime(date_str, "%Y-%m-%d")
        except:
            await query.edit_message_text(
            "❌ Erro ao processar data. Tente novamente.",
            reply_markup=self.keyboards.back_button()
        )
        return
    
        # Busca horários disponíveis
        apt_service = AppointmentService(db)
        available_slots = apt_service.get_available_slots(
            professional_id=professional_id,
            date=selected_date,
            service_id=service_id
    )
    
        if not available_slots:
            await query.edit_message_text(
                f"❌ Nenhum horário disponível em {selected_date.strftime('%d/%m/%Y')}\n\n"
                f"Por favor, escolha outra data.",
                reply_markup=self.keyboards.date_selection()
            )
            return
    
        # Atualiza estado
        self.user_states[user_id] = {
            "state": "selecting_time",
            "service_id": service_id,
            "professional_id": professional_id,
            "date": date_str
        }
        
        # Mostra horários disponíveis
        await query.edit_message_text(
            f"📅 Data: {selected_date.strftime('%d/%m/%Y')}\n\n"
            f"🕐 Escolha um horário:",
            reply_markup=self.keyboards.time_selection(available_slots)
    )