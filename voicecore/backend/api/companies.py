from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from db.database import get_db
from db.models import Company
from db.schemas import CompanyCreate, CompanyResponse


router = APIRouter(prefix="/companies", tags=["companies"])


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    plan: Optional[str] = None
    phone_number: Optional[str] = None
    whatsapp_number: Optional[str] = None


@router.post("/", response_model=CompanyResponse)
async def create_company(
    company: CompanyCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        db_company = Company(**company.model_dump())
        db.add(db_company)
        await db.commit()
        await db.refresh(db_company)
        return db_company
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[CompanyResponse])
async def list_companies(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(
            select(Company)
            .order_by(Company.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        companies = result.scalars().all()
        return companies
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(Company).where(Company.id == company_id))
        company = result.scalar_one_or_none()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        return company
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: int,
    company_update: CompanyUpdate,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(Company).where(Company.id == company_id))
        company = result.scalar_one_or_none()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        update_data = company_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                setattr(company, key, value)
        
        await db.commit()
        await db.refresh(company)
        return company
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{company_id}")
async def delete_company(
    company_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(Company).where(Company.id == company_id))
        company = result.scalar_one_or_none()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        await db.delete(company)
        await db.commit()
        return {"message": "Company deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
