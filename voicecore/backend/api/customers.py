from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel

from db.database import get_db
from db.models import Customer


router = APIRouter(prefix="/customers", tags=["customers"])


class CustomerCreate(BaseModel):
    company_id: int
    phone: str
    name: Optional[str] = None
    notes: Optional[str] = None


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    notes: Optional[str] = None


class CustomerResponse(BaseModel):
    id: int
    company_id: int
    phone: str
    name: Optional[str]
    notes: Optional[str]
    last_call_at: Optional[str]
    total_calls: int

    class Config:
        from_attributes = True


@router.post("/", response_model=CustomerResponse)
async def create_customer(
    customer: CustomerCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        existing = await db.execute(
            select(Customer).where(
                Customer.phone == customer.phone,
                Customer.company_id == customer.company_id
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Customer already exists")
        
        db_customer = Customer(**customer.model_dump())
        db.add(db_customer)
        await db.commit()
        await db.refresh(db_customer)
        return db_customer
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[CustomerResponse])
async def list_customers(
    company_id: int,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(
            select(Customer)
            .where(Customer.company_id == company_id)
            .order_by(Customer.last_call_at.desc().nullslast())
            .limit(limit)
            .offset(offset)
        )
        customers = result.scalars().all()
        return customers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(Customer).where(Customer.id == customer_id))
        customer = result.scalar_one_or_none()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return customer
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    customer_update: CustomerUpdate,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(Customer).where(Customer.id == customer_id))
        customer = result.scalar_one_or_none()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        update_data = customer_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                setattr(customer, key, value)
        
        await db.commit()
        await db.refresh(customer)
        return customer
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{customer_id}")
async def delete_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(Customer).where(Customer.id == customer_id))
        customer = result.scalar_one_or_none()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        await db.delete(customer)
        await db.commit()
        return {"message": "Customer deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-phone/{phone}")
async def get_customer_by_phone(
    phone: str,
    company_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(
            select(Customer).where(
                Customer.phone == phone,
                Customer.company_id == company_id
            )
        )
        customer = result.scalar_one_or_none()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return customer
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
