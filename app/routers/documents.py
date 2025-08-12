from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import base64
import json

from app.db import SessionLocal
from app import models

router = APIRouter(prefix="/documents", tags=["Documents"])

async def get_db():
    async with SessionLocal() as session:
        yield session

def _safe_json(s: Optional[str]) -> dict:
    if not s:
        return {}
    try:
        return json.loads(s)
    except Exception:
        raise HTTPException(status_code=400, detail="attrs must be valid JSON")

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    contact_id: Optional[int] = Form(None),
    property_id: Optional[int] = Form(None),
    transaction_id: Optional[int] = Form(None),
    attrs: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
):
    # Read file bytes
    content = await file.read()
    data_b64 = base64.b64encode(content).decode("utf-8")
    meta = _safe_json(attrs)
    meta.update({
        "data_b64": data_b64,           # store file bytes in DB (base64)
        "size": len(content)
    })

    doc = models.Document(
        filename=file.filename,
        mime_type=file.content_type or "application/octet-stream",
        contact_id=contact_id,
        property_id=property_id,
        transaction_id=transaction_id,
        attrs=meta,
        url=None,  # not used in this beta
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return {
        "id": doc.id,
        "filename": doc.filename,
        "mime_type": doc.mime_type,
        "size": doc.attrs.get("size"),
        "contact_id": doc.contact_id,
        "property_id": doc.property_id,
        "transaction_id": doc.transaction_id,
        "download_url": f"/documents/{doc.id}/download"
    }

@router.get("/")
async def list_documents(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(models.Document))
    docs = res.scalars().all()
    out = []
    for d in docs:
        out.append({
            "id": d.id,
            "filename": d.filename,
            "mime_type": d.mime_type,
            "size": (d.attrs or {}).get("size"),
            "contact_id": d.contact_id,
            "property_id": d.property_id,
            "transaction_id": d.transaction_id,
            "download_url": f"/documents/{d.id}/download"
        })
    return out

@router.get("/{doc_id}/download")
async def download_document(doc_id: int, db: AsyncSession = Depends(get_db)):
    doc = (await db.execute(select(models.Document).where(models.Document.id == doc_id))).scalars().first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    data_b64 = (doc.attrs or {}).get("data_b64")
    if not data_b64:
        raise HTTPException(status_code=400, detail="No file content stored")
    raw = base64.b64decode(data_b64.encode("utf-8"))
    return StreamingResponse(
        iter([raw]),
        media_type=doc.mime_type or "application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{doc.filename}"'}
    )
