from typing import Optional, Any, Dict
from sqlalchemy import String, Integer, ForeignKey, Float, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from .db import Base

class Contact(Base):
    __tablename__ = "contacts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String(50), default="new")
    # You can add any custom fields here without changing the database schema
    attrs: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)

    transactions = relationship("Transaction", back_populates="contact")

class Property(Base):
    __tablename__ = "properties"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    address: Mapped[str] = mapped_column(String(255))
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state_province: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, default="Canada")
    status: Mapped[Optional[str]] = mapped_column(String(50), default="prospect")
    attrs: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)

    transactions = relationship("Transaction", back_populates="property")

class Transaction(Base):
    __tablename__ = "transactions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    contact_id: Mapped[int] = mapped_column(ForeignKey("contacts.id"))
    property_id: Mapped[int] = mapped_column(ForeignKey("properties.id"))
    side: Mapped[str] = mapped_column(String(20), default="buy")   # buy / sell / lease
    stage: Mapped[str] = mapped_column(String(32), default="lead") # lead / showing / offer / conditional / pending / closed / fallen_through
    offer_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    close_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    attrs: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)

    contact = relationship("Contact", back_populates="transactions")
    property = relationship("Property", back_populates="transactions")

class Document(Base):
    __tablename__ = "documents"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(String(255))
    url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # for S3/Supabase later
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    contact_id: Mapped[Optional[int]] = mapped_column(ForeignKey("contacts.id"), nullable=True)
    property_id: Mapped[Optional[int]] = mapped_column(ForeignKey("properties.id"), nullable=True)
    transaction_id: Mapped[Optional[int]] = mapped_column(ForeignKey("transactions.id"), nullable=True)
    attrs: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
