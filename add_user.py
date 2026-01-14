import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.db.models import User, UserRole, ClientProfile

def add_user():
    db = SessionLocal()
    
    try:
        telegram_id = input("Digite seu Telegram ID (obtenha em @userinfobot): ")
        name = input("Digite seu nome: ")
        
        # Criar usuário
        user = User(
            telegram_id=telegram_id,
            name=name,
            role=UserRole.CLIENT
        )
        db.add(user)
        db.flush()
        
        # Criar perfil
        profile = ClientProfile(user_id=user.id)
        db.add(profile)
        db.commit()
        
        print(f"\n✅ Usuário '{name}' cadastrado com sucesso!")
        print(f"   Telegram ID: {telegram_id}")
        print(f"   Role: CLIENT")
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_user()