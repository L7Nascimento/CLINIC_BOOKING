"""
Script para popular o banco de dados
Execute: python seed.py
"""
import sys
import os

# Adiciona diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal, init_db
from app.db.models import (
    User, UserRole, Service, ProfessionalProfile,
    ProfessionalSchedule, ClientProfile
)

def seed_database():
    """Popula banco de dados com dados iniciais"""
    
    print("🔧 Inicializando banco de dados...")
    init_db()
    
    db = SessionLocal()
    
    try:
        print("📦 Criando dados iniciais...\n")
        
        # 1. Criar Serviços
        print("💼 Criando serviços...")
        services_data = [
            {
                "name": "Corte de Cabelo Masculino",
                "description": "Corte tradicional ou moderno",
                "price": 35.00,
                "duration_minutes": 30
            },
            {
                "name": "Corte de Cabelo Feminino",
                "description": "Corte com lavagem e escovação",
                "price": 60.00,
                "duration_minutes": 60
            },
            {
                "name": "Barba Completa",
                "description": "Barba com acabamento profissional",
                "price": 25.00,
                "duration_minutes": 20
            },
            {
                "name": "Corte + Barba",
                "description": "Combo completo",
                "price": 55.00,
                "duration_minutes": 45
            },
            {
                "name": "Coloração",
                "description": "Coloração completa",
                "price": 120.00,
                "duration_minutes": 90
            },
            {
                "name": "Hidratação Capilar",
                "description": "Tratamento intensivo",
                "price": 45.00,
                "duration_minutes": 40
            },
            {
                "name": "Penteado",
                "description": "Penteado para eventos",
                "price": 80.00,
                "duration_minutes": 60
            }
        ]
        
        services = []
        for service_data in services_data:
            service = Service(**service_data)
            db.add(service)
            services.append(service)
            print(f"  ✓ {service_data['name']} - R$ {service_data['price']:.2f}")
        
        db.commit()
        
        # 2. Criar Usuário Admin
        print("\n👑 Criando usuário admin...")
        admin_user = User(
            telegram_id="SEU_ID_AQUI",  # ⚠️ COLOQUE SEU TELEGRAM ID AQUI!
            name="Melissa",
            role=UserRole.ADMIN,
            email="melissa@exemplo.com",
            phone="(11) 99999-9999"
        )
        db.add(admin_user)
        db.commit()
        print(f"  ✓ Admin criado: {admin_user.name}")
        
        if admin_user.telegram_id == "7084688460":
            print(f"  ⚠️  ATENÇÃO: Substitua 'SEU_ID_AQUI' pelo seu Telegram ID real!")
            print(f"  ℹ️  Obtenha em: @userinfobot no Telegram")
        
        # 3. Criar Profissionais
        print("\n👨‍💼 Criando profissionais...")
        professionals_data = [
            {
                "name": "João Silva",
                "telegram_id": "111111111",
                "specialty": "Barbeiro Especialista",
                "commission": 60.0
            },
            {
                "name": "Maria Santos",
                "telegram_id": "222222222",
                "specialty": "Cabeleireira",
                "commission": 55.0
            },
            {
                "name": "Pedro Costa",
                "telegram_id": "333333333",
                "specialty": "Barbeiro",
                "commission": 50.0
            }
        ]
        
        for prof_data in professionals_data:
            user = User(
                telegram_id=prof_data["telegram_id"],
                name=prof_data["name"],
                role=UserRole.PROFESSIONAL,
                phone=f"(11) 9{prof_data['telegram_id'][:4]}-{prof_data['telegram_id'][4:8]}"
            )
            db.add(user)
            db.flush()
            
            profile = ProfessionalProfile(
                user_id=user.id,
                specialty=prof_data["specialty"],
                commission_percentage=prof_data["commission"]
            )
            db.add(profile)
            db.flush()
            
            profile.services = services
            
            # Agenda Segunda a Sexta, 8h-18h
            for day in range(5):
                schedule = ProfessionalSchedule(
                    professional_id=profile.id,
                    day_of_week=day,
                    start_time="08:00",
                    end_time="18:00"
                )
                db.add(schedule)
            
            # Sábado 8h-13h
            saturday = ProfessionalSchedule(
                professional_id=profile.id,
                day_of_week=5,
                start_time="08:00",
                end_time="13:00"
            )
            db.add(saturday)
            
            print(f"  ✓ {prof_data['name']} - {prof_data['specialty']}")
        
        db.commit()
        
        # 4. Criar clientes de exemplo
        print("\n👥 Criando clientes de exemplo...")
        clients_data = [
            {"name": "Carlos Oliveira", "telegram_id": "444444444"},
            {"name": "Ana Paula", "telegram_id": "555555555"},
            {"name": "Roberto Alves", "telegram_id": "666666666"}
        ]
        
        for client_data in clients_data:
            user = User(
                telegram_id=client_data["telegram_id"],
                name=client_data["name"],
                role=UserRole.CLIENT,
                phone=f"(11) 9{client_data['telegram_id'][:4]}-{client_data['telegram_id'][4:8]}"
            )
            db.add(user)
            db.flush()
            
            profile = ClientProfile(user_id=user.id)
            db.add(profile)
            
            print(f"  ✓ {client_data['name']}")
        
        db.commit()
        
        # Resumo Final
        print("\n" + "="*60)
        print("✅ Banco de dados populado com sucesso!")
        print("="*60)
        print(f"\n📊 Resumo:")
        print(f"  • {len(services_data)} serviços")
        print(f"  • {len(professionals_data)} profissionais")
        print(f"  • {len(clients_data)} clientes de exemplo")
        print(f"  • 1 administrador")
        
        print(f"\n🚀 Próximos passos:")
        print(f"  1. Edite seed.py e coloque seu Telegram ID")
        print(f"  2. Execute: python seed.py (novamente)")
        print(f"  3. Execute: python run.py")
        print(f"  4. Teste no Telegram!")
        
    except Exception as e:
        print(f"\n❌ Erro ao popular banco: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()