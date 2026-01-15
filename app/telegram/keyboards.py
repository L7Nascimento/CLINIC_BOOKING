from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

class Keyboards:
    """Teclados interativos modernos para o bot"""
    
    @staticmethod
    def main_menu(role: str = "client"):
        """Menu principal baseado no papel do usuário"""
        if role == "client":
            keyboard = [
                [InlineKeyboardButton("📅 Novo Agendamento", callback_data="new_appointment")],
                [InlineKeyboardButton("📋 Meus Agendamentos", callback_data="my_appointments")],
                [InlineKeyboardButton("💇‍♂️ Nossos Serviços", callback_data="view_services")],
                [InlineKeyboardButton("👨‍💼 Nossos Profissionais", callback_data="view_professionals")],
                [InlineKeyboardButton("💬 Falar com Gerência", callback_data="contact_management")],
                [InlineKeyboardButton("⚙️ Meu Perfil", callback_data="my_profile")]
            ]
        elif role == "professional":
            keyboard = [
                [InlineKeyboardButton("📊 Minha Agenda Hoje", callback_data="prof_today_schedule")],
                [InlineKeyboardButton("📈 Panorama da Semana", callback_data="prof_week_overview")],
                [InlineKeyboardButton("➕ Adicionar Cliente", callback_data="prof_add_client")],
                [InlineKeyboardButton("❌ Cancelar Horário", callback_data="prof_cancel_appointment")],
                [InlineKeyboardButton("💰 Meus Ganhos", callback_data="prof_earnings")],
                [InlineKeyboardButton("⚙️ Configurações", callback_data="prof_settings")]
            ]
        else:  # admin
            keyboard = [
                [InlineKeyboardButton("👥 Gerenciar Usuários", callback_data="admin_users")],
                [InlineKeyboardButton("👨‍💼 Gerenciar Profissionais", callback_data="admin_professionals")],
                [InlineKeyboardButton("💼 Gerenciar Serviços", callback_data="admin_services")],
                [InlineKeyboardButton("📊 Relatórios", callback_data="admin_reports")],
                [InlineKeyboardButton("💰 Faturamento", callback_data="admin_revenue")],
                [InlineKeyboardButton("⚙️ Configurações", callback_data="admin_settings")]
            ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def service_selection(services: list):
        """Teclado para seleção de serviços"""
        keyboard = []
        for service in services:
            keyboard.append([
                InlineKeyboardButton(
                    f"{service['name']} - R$ {service['price']:.2f}",
                    callback_data=f"service_{service['id']}"
                )
            ])
        keyboard.append([InlineKeyboardButton("« Voltar", callback_data="back_to_menu")])
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def professional_selection(professionals: list):
        """Teclado para seleção de profissionais"""
        keyboard = []
        for prof in professionals:
            availability = "✅" if prof.get('is_available') else "🔴"
            keyboard.append([
                InlineKeyboardButton(
                    f"{availability} {prof['name']} - {prof.get('specialty', 'Geral')}",
                    callback_data=f"professional_{prof['id']}"
                )
            ])
        keyboard.append([InlineKeyboardButton("« Voltar", callback_data="back_to_menu")])
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def date_selection():
        """Teclado para seleção de data (próximos 7 dias)"""
        from datetime import datetime, timedelta
        
        keyboard = []
        today = datetime.now()
        
        for i in range(7):
            date = today + timedelta(days=i)
            day_name = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"][date.weekday()]
            date_str = date.strftime("%d/%m")
            
            keyboard.append([
                InlineKeyboardButton(
                    f"{day_name} {date_str}",
                    callback_data=f"date_{date.strftime('%Y-%m-%d')}"
                )
            ])
        
        keyboard.append([InlineKeyboardButton("« Voltar", callback_data="back_to_menu")])
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    @staticmethod
    def time_selection(available_times: list):
        keyboard = []
        row = []

        for i, time_str in enumerate(available_times):
            row.append(
                InlineKeyboardButton(
                    time_str,
                    callback_data=f"time_{time_str}"
                )
            )

            if (i + 1) % 3 == 0:
                keyboard.append(row)
                row = []

        if row:
            keyboard.append(row)

        keyboard.append([InlineKeyboardButton("« Voltar", callback_data="select_date")])
        return InlineKeyboardMarkup(keyboard)

    
    @staticmethod
    def appointment_actions(appointment_id: int, can_cancel: bool = True):
        """Ações para um agendamento"""
        keyboard = []
        
        if can_cancel:
            keyboard.append([
                InlineKeyboardButton("❌ Cancelar", callback_data=f"cancel_apt_{appointment_id}")
            ])
        
        keyboard.extend([
            [InlineKeyboardButton("📍 Ver Detalhes", callback_data=f"details_apt_{appointment_id}")],
            [InlineKeyboardButton("🔔 Reagendar", callback_data=f"reschedule_apt_{appointment_id}")],
            [InlineKeyboardButton("« Voltar", callback_data="my_appointments")]
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def confirm_action(action: str, data: str):
        """Confirmação de ação"""
        keyboard = [
            [
                InlineKeyboardButton("✅ Sim, confirmar", callback_data=f"confirm_{action}_{data}"),
                InlineKeyboardButton("❌ Cancelar", callback_data="cancel_action")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def admin_crud_menu(entity: str):
        """Menu CRUD para admin"""
        keyboard = [
            [InlineKeyboardButton(f"➕ Adicionar {entity}", callback_data=f"add_{entity}")],
            [InlineKeyboardButton(f"📝 Editar {entity}", callback_data=f"edit_{entity}")],
            [InlineKeyboardButton(f"🗑️ Remover {entity}", callback_data=f"remove_{entity}")],
            [InlineKeyboardButton(f"📋 Listar {entity}", callback_data=f"list_{entity}")],
            [InlineKeyboardButton("« Voltar", callback_data="back_to_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def report_period_selection():
        """Seleção de período para relatórios"""
        keyboard = [
            [InlineKeyboardButton("📅 Hoje", callback_data="report_today")],
            [InlineKeyboardButton("📅 Esta Semana", callback_data="report_week")],
            [InlineKeyboardButton("📅 Este Mês", callback_data="report_month")],
            [InlineKeyboardButton("📅 Este Ano", callback_data="report_year")],
            [InlineKeyboardButton("📅 Personalizado", callback_data="report_custom")],
            [InlineKeyboardButton("« Voltar", callback_data="back_to_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def late_client_options():
        """Opções quando cliente avisa atraso"""
        keyboard = [
            [InlineKeyboardButton("⏰ Vou atrasar 15 min", callback_data="late_15")],
            [InlineKeyboardButton("⏰ Vou atrasar 30 min", callback_data="late_30")],
            [InlineKeyboardButton("🔄 Reagendar", callback_data="reschedule_late")],
            [InlineKeyboardButton("❌ Cancelar", callback_data="cancel_late")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def back_button():
        """Botão de voltar simples"""
        return InlineKeyboardMarkup([[
            InlineKeyboardButton("« Voltar ao Menu", callback_data="back_to_menu")
        ]])