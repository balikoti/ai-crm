from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db import engine
from app import models
from app.routers import contacts, properties, transactions, search
from app.routers import ui, documents  # <-- added documents

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

# API routers
app.include_router(contacts.router)
app.include_router(properties.router)
app.include_router(transactions.router)
app.include_router(search.router)

# UI + Documents
app.include_router(ui.router)
app.include_router(documents.router)
