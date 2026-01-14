"""
Script para popular o banco de dados com dados iniciais
Execute: python scripts/seed_database.py
"""

import sys
from pathlib import Path
"""
Script para popular o banco de dados com dados iniciais
Execute: python scripts/seed_database.py
"""

"""
Script para popular o banco de dados com dados iniciais
Execute: python scripts/seed_database.py
"""

import sys
import os
from pathlib import Path

# Adiciona o diretório raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

# Agora pode importar
from app.db.session import SessionLocal, init_db
from app.db.models import (
    User, UserRole, Service, ProfessionalProfile,
    ProfessionalSchedule, ClientProfile
)

# Agora os imports normais
from app.db.session import SessionLocal, init_db
from app.db.models import (
    User, UserRole, Service, ProfessionalProfile,
    ProfessionalSchedule, ClientProfile
)

# Adiciona o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

from app.db.session import SessionLocal, init_db
from app.db.models import (
    User, UserRole, Service, ProfessionalProfile,
    ProfessionalSchedule, ClientProfile
)

def seed_database():
    """Popula banco de dados com dados iniciais"""
    
    # Inicializa banco
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
        
        # 2. Criar Usuário Admin (exemplo)
        print("\n👑 Criando usuário admin de exemplo...")
        admin_user = User(
            telegram_id="7084688460",  # Substitua pelo ID real
            name="Leandro",
            role=UserRole.ADMIN,
            email="admin@exemplo.com",
            phone="(19) 981037736"
        )
        db.add(admin_user)
        db.commit()
        print(f"  ✓ Admin criado: {admin_user.name}")
        print(f"  ⚠️  IMPORTANTE: Substitua o telegram_id '000000000' pelo seu ID real!")
        
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
        
        professionals = []
        for prof_data in professionals_data:
            # Criar usuário
            user = User(
                telegram_id=prof_data["telegram_id"],
                name=prof_data["name"],
                role=UserRole.PROFESSIONAL,
                phone=f"(11) 9{prof_data['telegram_id'][:4]}-{prof_data['telegram_id'][4:8]}"
            )
            db.add(user)
            db.flush()
            
            # Criar perfil profissional
            profile = ProfessionalProfile(
                user_id=user.id,
                specialty=prof_data["specialty"],
                commission_percentage=prof_data["commission"]
            )
            db.add(profile)
            db.flush()
            
            # Adicionar todos os serviços ao profissional
            profile.services = services
            
            # Criar agenda padrão (Segunda a Sexta, 8h-18h)
            for day in range(5):  # 0-4 = Segunda a Sexta
                schedule = ProfessionalSchedule(
                    professional_id=profile.id,
                    day_of_week=day,
                    start_time="08:00",
                    end_time="18:00"
                )
                db.add(schedule)
            
            # Sábado meio período
            saturday_schedule = ProfessionalSchedule(
                professional_id=profile.id,
                day_of_week=5,
                start_time="08:00",
                end_time="13:00"
            )
            db.add(saturday_schedule)
            
            professionals.append(profile)
            print(f"  ✓ {prof_data['name']} - {prof_data['specialty']}")
        
        db.commit()
        
        # 4. Criar alguns clientes de exemplo
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
        
        # Resumo
        print("\n" + "="*50)
        print("✅ Banco de dados populado com sucesso!")
        print("="*50)
        print(f"\n📊 Resumo:")
        print(f"  • {len(services_data)} serviços criados")
        print(f"  • {len(professionals_data)} profissionais criados")
        print(f"  • {len(clients_data)} clientes de exemplo")
        print(f"  • 1 administrador")
        
        print(f"\n⚠️  IMPORTANTE:")
        print(f"  1. Substitua os telegram_id fictícios pelos IDs reais")
        print(f"  2. Para obter seu Telegram ID, use o bot @userinfobot")
        print(f"  3. Configure as variáveis de ambiente no arquivo .env")
        
        print(f"\n🚀 Próximos passos:")
        print(f"  1. Configure seu .env com TELEGRAM_BOT_TOKEN e ANTHROPIC_API_KEY")
        print(f"  2. Execute: python app/main.py")
        print(f"  3. Abra seu bot no Telegram e envie /start")
        
    except Exception as e:
        print(f"\n❌ Erro ao popular banco de dados: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()