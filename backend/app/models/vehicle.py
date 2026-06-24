from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    make = Column(String, nullable=False, index=True)
    model = Column(String, nullable=False, index=True)
    trim = Column(String, nullable=True)
    year = Column(Integer, nullable=False)
    category = Column(String, nullable=True)  # EV, SUV, Luxury, Truck, Sedan
    created_at = Column(DateTime, default=datetime.utcnow)

    lease_programs = relationship("LeaseProgram", back_populates="vehicle", cascade="all, delete-orphan")
    inventory_metrics = relationship("InventoryMetric", back_populates="vehicle", cascade="all, delete-orphan")
    deal_evidence = relationship("DealEvidence", back_populates="vehicle", cascade="all, delete-orphan")
    hackability_scores = relationship("HackabilityScore", back_populates="vehicle", cascade="all, delete-orphan")
