from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class LeaseProgram(Base):
    __tablename__ = "lease_programs"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False, index=True)
    program_month = Column(Integer, nullable=False)
    program_year = Column(Integer, nullable=False)
    term = Column(Integer, nullable=False)
    mileage = Column(Integer, nullable=False)
    residual_percent = Column(Float, nullable=True)
    money_factor = Column(Float, nullable=True)
    lease_cash = Column(Float, default=0.0)
    loyalty_cash = Column(Float, default=0.0)
    conquest_cash = Column(Float, default=0.0)
    military_cash = Column(Float, default=0.0)
    college_cash = Column(Float, default=0.0)
    regional_notes = Column(Text, nullable=True)
    source = Column(String, nullable=True)
    source_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    vehicle = relationship("Vehicle", back_populates="lease_programs")
