from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from ..db import SessionLocal

router = APIRouter(prefix="/search", tags=["Search"])

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.get("/contacts/by-attr")
async def contacts_by_attr(key: str = Query(...), equals: str = Query(...), db: AsyncSession = Depends(get_db)):
    sql = text("SELECT * FROM contacts WHERE attrs->>:key = :equals")
    res = await db.execute(sql, {"key": key, "equals": equals})
    return [dict(r._mapping) for r in res]

@router.get("/properties/number-attr-gte")
async def properties_number_attr_gte(key: str = Query(...), gte: float = Query(...), db: AsyncSession = Depends(get_db)):
    sql = text("SELECT * FROM properties WHERE (attrs->>:key)::numeric >= :gte")
    res = await db.execute(sql, {"key": key, "gte": gte})
    return [dict(r._mapping) for r in res]
