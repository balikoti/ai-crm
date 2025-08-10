from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db import SessionLocal
from app import models, schemas

router = APIRouter(prefix="/contacts", tags=["Contacts"])

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.post("/", response_model=schemas.ContactOut)
async def create_contact(contact: schemas.ContactCreate, db: AsyncSession = Depends(get_db)):
    new_contact = models.Contact(**contact.dict())
    db.add(new_contact)
    await db.commit()
    await db.refresh(new_contact)
    return new_contact

@router.get("/", response_model=list[schemas.ContactOut])
async def list_contacts(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(models.Contact))
    return res.scalars().all()
