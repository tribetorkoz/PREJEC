import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from db.database import AsyncSessionLocal, init_db
from db.models import Company, Agent, Customer, Call, AdminUser
from sqlalchemy import select
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def seed_data():
    await init_db()
    
    async with AsyncSessionLocal() as session:
        print("Creating super admin user...")
        result = await session.execute(
            select(AdminUser).where(AdminUser.email == "admin@voicecore.ai")
        )
        existing_admin = result.scalar_one_or_none()
        
        if existing_admin:
            print(f"   - Admin already exists: admin@voicecore.ai")
        else:
            admin = AdminUser(
                email="admin@voicecore.ai",
                password_hash=pwd_context.hash("VoiceCore2024!"),
                name="Super Admin",
                role="super_admin",
                is_active=True
            )
            session.add(admin)
            await session.commit()
            print(f"   - Admin created: admin@voicecore.ai / VoiceCore2024!")
        
        print("Creating demo company...")
        result = await session.execute(
            select(Company).where(Company.email == "demo@voicecore.ai")
        )
        existing_company = result.scalar_one_or_none()
        
        if existing_company:
            print(f"   - Demo company already exists")
            company = existing_company
        else:
            company = Company(
                name="Demo Company",
                email="demo@voicecore.ai",
                plan="business",
                phone_number="+1234567890",
                whatsapp_number="whatsapp:+1234567890"
            )
            session.add(company)
            await session.commit()
            await session.refresh(company)
            print(f"   - Demo company created")
        
        print("Creating demo agent...")
        result = await session.execute(
            select(Agent).where(Agent.company_id == company.id)
        )
        existing_agent = result.scalar_one_or_none()
        
        if not existing_agent:
            agent = Agent(
                company_id=company.id,
                name="Sarah",
                language="auto",
                voice_id="rachel",
                system_prompt="""You are Sarah, a professional voice assistant for Demo Company.
You are polite, helpful, and concise.
You help customers with:
- Booking appointments
- Checking business hours
- Answering general questions
Always confirm appointments before saving.""",
                is_active=True
            )
            session.add(agent)
            await session.commit()
            print(f"   - Demo agent created")
        else:
            print(f"   - Demo agent already exists")
        
        print("Creating demo customers...")
        for customer_data in [
            {"phone": "+1234567891", "name": "John Smith"},
            {"phone": "+1234567892", "name": "Maria Garcia"},
            {"phone": "+1234567893", "name": "Ahmed Hassan"},
            {"phone": "+1234567894", "name": "Sophie Martin"},
            {"phone": "+1234567895", "name": "Ali Ahmed"},
        ]:
            result = await session.execute(
                select(Customer).where(Customer.phone == customer_data["phone"])
            )
            if not result.scalar_one_or_none():
                customer = Customer(
                    company_id=company.id,
                    phone=customer_data["phone"],
                    name=customer_data["name"],
                    total_calls=0
                )
                session.add(customer)
        
        await session.commit()
        
        print("\n========================================")
        print(" VoiceCore seeded successfully!")
        print("========================================")
        print(f" SUPER ADMIN LOGIN:")
        print(f"   Email:    admin@voicecore.ai")
        print(f"   Password: VoiceCore2024!")
        print(f"\n URL: http://localhost:3000/super-admin/login")
        print("========================================")


if __name__ == "__main__":
    asyncio.run(seed_data())
