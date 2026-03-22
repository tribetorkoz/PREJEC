import asyncio
from sqlalchemy import text
from db.database import engine, Base
from db.models import User, Company, Agent, Call, Customer

async def init_db():
    print("Initializing Database...")
    async with engine.begin() as conn:
        # Create tables
        await conn.run_sync(Base.metadata.create_all)
        
        # Check if 'sentiment_score' column exists in 'calls' table
        try:
            # PostgreSQL specific check
            result = await conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='calls' AND column_name='sentiment_score';
            """))
            has_score = (await result.scalar()) is not None
            
            if not has_score:
                print("Migrating: Adding sentiment_score to calls table...")
                await conn.execute(text("ALTER TABLE calls ADD COLUMN sentiment_score FLOAT;"))
                print("Migration complete.")
        except Exception as e:
            # Fallback if SQLite or error
            try:
                await conn.execute(text("ALTER TABLE calls ADD COLUMN sentiment_score FLOAT;"))
                print("Migration complete (Fallback).")
            except Exception:
                pass # Column likely already exists

    print("Database Initialization Complete.")

if __name__ == "__main__":
    asyncio.run(init_db())
