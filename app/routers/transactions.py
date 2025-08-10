from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..db import SessionLocal
from .. import models, schemas

router = APIRouter(prefix="/transactions", tags=["Transactions"])

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.post("/", response_model=schemas.TransactionOut)
async def create_transaction(payload: schemas.TransactionCreate, db: AsyncSession = Depends(get_db)):
    tx = models.Transaction(**payload.dict())
    db.add(tx)
    await db.commit()
    await db.refresh(tx)
    return tx

@router.get("/", response_model=list[schemas.TransactionOut])
async def list_transactions(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(models.Transaction))
    return res.scalars().all()
