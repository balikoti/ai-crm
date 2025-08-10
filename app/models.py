from sqlalchemy import Column, Integer, String
from .db import Base

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    tag = Column(String, index=True)
    birthday = Column(String, index=True)
    status = Column(String, index=True)
