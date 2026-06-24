from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.db.base import Base


class Store(Base):
    __tablename__ = "stores"
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="store")
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, nullable=False)
    instagram = Column(String, nullable=True)
    telegram = Column(String, nullable=True)
    whatsapp = Column(String, nullable=True)
    address = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    bale = Column(String, nullable=True)
    eita = Column(String, nullable=True)
    rubika = Column(String, nullable=True)
