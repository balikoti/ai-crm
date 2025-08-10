from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..db import SessionLocal
from .. import models, schemas

router = APIRouter(prefix="/properties", tags=["Properties"])

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.post("/", response_model=schemas.PropertyOut)
async def create_property(payload: schemas.PropertyCreate, db: AsyncSession = Depends(get_db)):
    p = models.Property(**payload.dict())
    db.add(p)
    await db.commit()
    await db.refresh(p)
    return p

@router.get("/", response_model=list[schemas.PropertyOut])
async def list_properties(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(models.Property))
    return res.scalars().all()
