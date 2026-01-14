import anthropic
from app.config import settings
from typing import List, Dict, Optional
import json

class AIService:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.CLAUDE_MODEL
        
    async def chat(self, user_message: str, context: Optional[Dict] = None, conversation_history: Optional[List[Dict]] = None) -> str:
        """
        Processa mensagem do usuário com Claude IA
        
        Args:
            user_message: Mensagem do usuário
            context: Contexto adicional (dados do usuário, agendamentos, etc)
            conversation_history: Histórico da conversa
        """
        system_prompt = self._build_system_prompt(context)
        
        messages = conversation_history or []
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                system=system_prompt,
                messages=messages
            )
            
            return response.content[0].text
        except Exception as e:
            return f"Desculpe, ocorreu um erro ao processar sua mensagem. Por favor, tente novamente."
    
    def _build_system_prompt(self, context: Optional[Dict] = None) -> str:
        """Constrói o prompt do sistema com contexto"""
        base_prompt = f"""Você é um assistente virtual elegante e educado para um sistema de agendamento de clínicas, salões e barbearias.

DIRETRIZES DE COMPORTAMENTO:
- Seja sempre educado, cordial e profissional
- Use uma linguagem clara e objetiva
- Responda de forma concisa mas completa
- Mostre empatia com os clientes
- Ofereça sempre alternativas quando algo não for possível

SUAS CAPACIDADES:
- Agendar horários para clientes
- Cancelar agendamentos
- Sugerir horários disponíveis
- Cadastrar novos clientes
- Fornecer informações sobre serviços
- Responder dúvidas sobre o estabelecimento

Nome do estabelecimento: {settings.APP_NAME}
Horário de funcionamento: {settings.BUSINESS_HOURS_START} às {settings.BUSINESS_HOURS_END}
"""
        
        if context:
            if context.get("user_name"):
                base_prompt += f"\n\nCliente atual: {context['user_name']}"
            
            if context.get("available_services"):
                services = "\n".join([f"- {s['name']}: R$ {s['price']:.2f} ({s['duration_minutes']} min)" 
                                     for s in context['available_services']])
                base_prompt += f"\n\nServiços disponíveis:\n{services}"
            
            if context.get("user_appointments"):
                base_prompt += f"\n\nO cliente possui {len(context['user_appointments'])} agendamento(s) ativo(s)."
            
            if context.get("reliability_level"):
                base_prompt += f"\n\nNível de confiabilidade do cliente: {context['reliability_level']}"
        
        return base_prompt
    
    async def analyze_appointment_request(self, message: str) -> Dict:
        """
        Analisa uma mensagem para extrair intenção de agendamento
        Retorna estrutura JSON com os dados extraídos
        """
        prompt = f"""Analise a seguinte mensagem de um cliente e extraia as informações de agendamento:

Mensagem: "{message}"

Responda APENAS com um JSON válido contendo:
{{
    "intent": "schedule|cancel|info|other",
    "service_mentioned": "nome do serviço se mencionado",
    "professional_mentioned": "nome do profissional se mencionado",
    "date_mentioned": "data se mencionada (formato YYYY-MM-DD)",
    "time_mentioned": "horário se mencionado (formato HH:MM)"
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result_text = response.content[0].text.strip()
            # Remove markdown se presente
            if result_text.startswith("```json"):
                result_text = result_text[7:-3].strip()
            elif result_text.startswith("```"):
                result_text = result_text[3:-3].strip()
                
            return json.loads(result_text)
        except Exception as e:
            return {"intent": "other", "error": str(e)}
    
    async def generate_professional_summary(self, professional_data: Dict) -> str:
        """Gera resumo da agenda do profissional"""
        prompt = f"""Gere um resumo elegante e profissional da agenda para o profissional:

Dados:
- Nome: {professional_data.get('name')}
- Agendamentos hoje: {professional_data.get('appointments_today', 0)}
- Próximo horário: {professional_data.get('next_appointment', 'Nenhum')}
- Faturamento estimado hoje: R$ {professional_data.get('estimated_revenue', 0):.2f}
- Horários vagos: {professional_data.get('empty_slots', [])}

Crie uma mensagem motivadora e informativa em até 200 palavras."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except:
            return "Resumo da agenda não disponível no momento."
    
    async def generate_admin_report(self, business_data: Dict) -> str:
        """Gera relatório gerencial para o admin"""
        prompt = f"""Gere um relatório executivo conciso baseado nos seguintes dados do negócio:

Período: {business_data.get('period')}
- Total de agendamentos: {business_data.get('total_appointments')}
- Agendamentos completados: {business_data.get('completed')}
- Cancelamentos: {business_data.get('cancelled')}
- No-shows: {business_data.get('no_shows')}
- Faturamento total: R$ {business_data.get('revenue', 0):.2f}
- Serviço mais popular: {business_data.get('top_service')}
- Taxa de ocupação: {business_data.get('occupancy_rate', 0):.1f}%

Forneça insights e recomendações em até 300 palavras."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except:
            return "Relatório não disponível no momento."

# Instância global do serviço de IA
ai_service = AIService()