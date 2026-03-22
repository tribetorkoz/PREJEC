from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from datetime import datetime, timedelta
from db.database import get_db
from db.models import Call
from db.schemas import AnalyticsResponse


router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/", response_model=AnalyticsResponse)
async def get_analytics(
    company_id: int,
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    try:
        start_date = datetime.now() - timedelta(days=days)
        
        total_calls_result = await db.execute(
            select(func.count(Call.id))
            .where(Call.company_id == company_id)
            .where(Call.created_at >= start_date)
        )
        total_calls = total_calls_result.scalar() or 0
        
        total_duration_result = await db.execute(
            select(func.sum(Call.duration_seconds))
            .where(Call.company_id == company_id)
            .where(Call.created_at >= start_date)
        )
        total_duration = total_duration_result.scalar() or 0
        
        # Use sentiment_score (Float) instead of sentiment (String) for avg
        avg_sentiment_result = await db.execute(
            select(func.avg(Call.sentiment_score))
            .where(Call.company_id == company_id)
            .where(Call.created_at >= start_date)
            .where(Call.sentiment_score.isnot(None))
        )
        avg_sentiment_score = avg_sentiment_result.scalar()
        
        # Get sentiment breakdown (count per sentiment category)
        sentiment_result = await db.execute(
            select(Call.sentiment, func.count(Call.id))
            .where(Call.company_id == company_id)
            .where(Call.created_at >= start_date)
            .where(Call.sentiment.isnot(None))
            .group_by(Call.sentiment)
        )
        sentiment_breakdown = {row[0]: row[1] for row in sentiment_result.all() if row[0]}
        
        # Use a single query with GROUP BY for calls_by_day instead of N+1 queries
        calls_by_day_result = await db.execute(
            select(
                func.date(Call.created_at).label("day"),
                func.count(Call.id).label("count")
            )
            .where(Call.company_id == company_id)
            .where(Call.created_at >= start_date)
            .group_by(func.date(Call.created_at))
            .order_by(func.date(Call.created_at))
        )
        calls_by_day = {str(row.day): row.count for row in calls_by_day_result.all()}
        
        # Fill in missing days with 0
        for i in range(days):
            day = str((datetime.now() - timedelta(days=i)).date())
            if day not in calls_by_day:
                calls_by_day[day] = 0
        
        return AnalyticsResponse(
            total_calls=total_calls,
            total_duration=total_duration,
            avg_sentiment_score=avg_sentiment_score,
            sentiment_breakdown=sentiment_breakdown,
            calls_by_day=calls_by_day,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def get_summary(
    company_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        total_calls_result = await db.execute(
            select(func.count(Call.id)).where(Call.company_id == company_id)
        )
        total_calls = total_calls_result.scalar() or 0
        
        total_duration_result = await db.execute(
            select(func.sum(Call.duration_seconds)).where(Call.company_id == company_id)
        )
        total_duration = total_duration_result.scalar() or 0
        
        avg_duration_result = await db.execute(
            select(func.avg(Call.duration_seconds)).where(Call.company_id == company_id)
        )
        avg_duration = float(avg_duration_result.scalar() or 0)
        
        return {
            "total_calls": total_calls,
            "total_duration_seconds": total_duration,
            "avg_duration_seconds": round(avg_duration, 1),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
