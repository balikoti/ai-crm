from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import engine
from app import models
from app.routers import contacts, properties, transactions, search
from app.routers import ui, documents, ingest  # <- includes UI, Documents, and Ingest

app = FastAPI(title="Flexible AI CRM", version="0.1.0")

# CORS (lets the mini UI call the API from the same host)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # keep simple for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup (safe if already created)
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

# UI + Documents + Ingest
app.include_router(ui.router)
app.include_router(documents.router)
app.include_router(ingest.router)
