from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import engine
from . import models
from .routers import contacts, properties, transactions, search

app = FastAPI(title="Flexible AI CRM", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

@app.get("/health")
async def health():
    return {"ok": True}

app.include_router(contacts.router)
app.include_router(properties.router)
app.include_router(transactions.router)
app.include_router(search.router)
