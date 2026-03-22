from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from db.database import get_db
from db.models import Agent
from db.schemas import AgentCreate, AgentUpdate, AgentResponse


router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("/", response_model=AgentResponse)
async def create_agent(
    agent: AgentCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        db_agent = Agent(**agent.model_dump())
        db.add(db_agent)
        await db.commit()
        await db.refresh(db_agent)
        return db_agent
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[AgentResponse])
async def list_agents(
    company_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(
            select(Agent)
            .where(Agent.company_id == company_id)
            .order_by(Agent.created_at.desc())
        )
        agents = result.scalars().all()
        return agents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(Agent).where(Agent.id == agent_id))
        agent = result.scalar_one_or_none()
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        return agent
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: int,
    agent_update: AgentUpdate,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(Agent).where(Agent.id == agent_id))
        agent = result.scalar_one_or_none()
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Only update fields that were explicitly set (not None)
        update_data = agent_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(agent, key, value)
        
        await db.commit()
        await db.refresh(agent)
        return agent
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(Agent).where(Agent.id == agent_id))
        agent = result.scalar_one_or_none()
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        await db.delete(agent)
        await db.commit()
        return {"message": "Agent deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{agent_id}/toggle")
async def toggle_agent(
    agent_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(Agent).where(Agent.id == agent_id))
        agent = result.scalar_one_or_none()
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        agent.is_active = not agent.is_active
        await db.commit()
        await db.refresh(agent)
        return {"agent_id": agent.id, "is_active": agent.is_active}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
