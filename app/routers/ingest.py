from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, Tuple
import re

from app.db import SessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app import models

router = APIRouter(prefix="/ingest", tags=["Ingest"])

async def get_db():
    async with SessionLocal() as session:
        yield session

# ---------- Helpers ----------

EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(r"\b(?:\+?\d{1,3}[ -]?)?(?:\(?\d{3}\)?[ -]?)?\d{3}[ -]?\d{4}\b")
MONEY_RE = re.compile(r"\b(\$?\s?\d[\d,]*\.?\d*)\b")
BEDS_RE = re.compile(r"\b(\d+)\s*bed", re.I)
BATHS_RE = re.compile(r"\b(\d+)\s*bath", re.I)
ADDRESS_HINTS = [" st", " ave", " rd", " blvd", "street", "avenue", "road", "drive", "lane", "court", "unit", "apt", "suite"]

def looks_like_address(text: str) -> bool:
    t = text.lower()
    return any(h in t for h in ADDRESS_HINTS) or bool(re.search(r"\b\d{1,5}\s+\w+", t))

def extract_money(text: str) -> Optional[float]:
    m = MONEY_RE.search(text.replace(",", ""))
    if not m:
        return None
    raw = m.group(1).replace("$", "").replace(" ", "")
    try:
        return float(raw)
    except:
        return None

def guess_entity(text: str) -> Tuple[str, Dict[str, Any]]:
    """
    Returns (entity_guess, draft_payload)
    entity_guess in {"contact","property","transaction","unknown"}
    draft_payload holds fields we think we saw, plus attrs with original text.
    """
    t = text.strip()

    # Signals
    has_email = bool(EMAIL_RE.search(t))
    has_phone = bool(PHONE_RE.search(t))
    has_buy_sell = any(w in t.lower() for w in ["buy", "sell", "lease", "offer", "close", "offer price", "closing"])
    is_address = looks_like_address(t)
    price = extract_money(t)
    beds = BEDS_RE.search(t)
    baths = BATHS_RE.search(t)

    # CONTACT: name/email/phone/status words
    if ("contact" in t.lower()) or has_email or has_phone:
        draft = {
            "type": "contact",
            "first_name": None,
            "last_name": None,
            "email": EMAIL_RE.search(t).group(0) if has_email else None,
            "phone": PHONE_RE.search(t).group(0) if has_phone else None,
            "status": None,
            "attrs": {"note": t}
        }
        return "contact", draft

    # PROPERTY: address hints or bed/bath or price
    if ("property" in t.lower()) or is_address or beds or baths:
        draft = {
            "type": "property",
            "address": t if is_address else None,
            "city": None,
            "state_province": None,
            "country": "Canada",
            "status": "prospect",
            "attrs": {}
        }
        if beds:
            draft["attrs"]["bed"] = int(beds.group(1))
        if baths:
            draft["attrs"]["bath"] = int(baths.group(1))
        if price:
            draft["attrs"]["list_price"] = price
        if not is_address:
            draft["attrs"]["note"] = t
        return "property", draft

    # TRANSACTION: buy/sell/lease/offer/close + maybe price
    if ("transaction" in t.lower()) or has_buy_sell:
        side = "buy" if "buy" in t.lower() else ("sell" if "sell" in t.lower() else ("lease" if "lease" in t.lower() else "buy"))
        draft = {
            "type": "transaction",
            "contact_id": None,
            "property_id": None,
            "side": side,
            "stage": "lead",
            "offer_price": price if ("offer" in t.lower() and price) else None,
            "close_price": price if ("close" in t.lower() and price) else None,
            "attrs": {"note": t}
        }
        return "transaction", draft

    # Unknown → ask
    return "unknown", {"type": "unknown", "attrs": {"note": t}}

# ---------- Schemas ----------

class IngestRequest(BaseModel):
    text: str

class ConfirmRequest(BaseModel):
    choice: str  # "contact" | "property" | "transaction"
    draft: Dict[str, Any]

# ---------- Endpoints ----------

@router.post("")
async def ingest(req: IngestRequest, db: AsyncSession = Depends(get_db)):
    kind, draft = guess_entity(req.text)

    if kind == "unknown":
        return {
            "status": "ask",
            "question": "Should I save this as a contact, property, or transaction?",
            "options": ["contact", "property", "transaction"],
            "draft": draft,
        }

    # If we have a strong guess, but missing required IDs for a transaction, ask.
    if kind == "transaction":
        if draft.get("contact_id") is None or draft.get("property_id") is None:
            return {
                "status": "ask",
                "question": "I think this is a transaction. Please provide contact_id and property_id, or pick a different type.",
                "options": ["contact", "property", "transaction"],
                "draft": draft,
            }

    # If contact/property drafts are too empty, ask for confirmation.
    if kind in ("contact", "property"):
        return {
            "status": "ask",
            "question": f"I think this is a {kind}. Do you want me to save it?",
            "options": [kind, "cancel"],
            "draft": draft,
        }

    # Fallback (shouldn’t hit)
    return {"status": "ask", "question": "Not sure. Choose a type.", "options": ["contact","property","transaction"], "draft": draft}

@router.post("/confirm")
async def confirm(req: ConfirmRequest, db: AsyncSession = Depends(get_db)):
    choice = req.choice.lower().strip()
    draft = req.draft or {}

    if choice == "cancel":
        return {"status": "cancelled"}

    if choice == "contact":
        # Minimal required: first or last name — if neither, use text note.
        first = draft.get("first_name") or ""
        last = draft.get("last_name") or ""
        if not (first or last):
            first, last = "Unknown", "Contact"
        c = models.Contact(
            first_name=first,
            last_name=last,
            email=draft.get("email"),
            phone=draft.get("phone"),
            status=draft.get("status") or "new",
            attrs=draft.get("attrs") or {}
        )
        db.add(c)
        await db.commit()
        await db.refresh(c)
        return {"status": "created", "entity": "contact", "id": c.id}

    if choice == "property":
        addr = draft.get("address") or "Unknown address"
        p = models.Property(
            address=addr,
            city=draft.get("city"),
            state_province=draft.get("state_province"),
            country=draft.get("country") or "Canada",
            status=draft.get("status") or "prospect",
            attrs=draft.get("attrs") or {}
        )
        db.add(p)
        await db.commit()
        await db.refresh(p)
        return {"status": "created", "entity": "property", "id": p.id}

    if choice == "transaction":
        contact_id = draft.get("contact_id")
        property_id = draft.get("property_id")
        if not contact_id or not property_id:
            raise HTTPException(status_code=400, detail="transaction requires contact_id and property_id")
        tx = models.Transaction(
            contact_id=contact_id,
            property_id=property_id,
            side=draft.get("side") or "buy",
            stage=draft.get("stage") or "lead",
            offer_price=draft.get("offer_price"),
            close_price=draft.get("close_price"),
            attrs=draft.get("attrs") or {}
        )
        db.add(tx)
        await db.commit()
        await db.refresh(tx)
        return {"status": "created", "entity": "transaction", "id": tx.id}

    raise HTTPException(status_code=400, detail="invalid choice")
