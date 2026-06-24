from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class DealEvidence(Base):
    __tablename__ = "deal_evidence"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False, index=True)
    monthly_payment = Column(Float, nullable=True)
    effective_monthly = Column(Float, nullable=True)
    msrp = Column(Float, nullable=True)
    selling_price = Column(Float, nullable=True)
    discount_percent = Column(Float, nullable=True)
    das = Column(Float, nullable=True)
    term = Column(Integer, nullable=True)
    mileage = Column(Integer, nullable=True)
    region = Column(String, nullable=True)
    source = Column(String, nullable=True)
    source_url = Column(String, nullable=True)
    deal_date = Column(Date, nullable=True)
    leasehackr_score = Column(Float, nullable=True)
    raw_data = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    vehicle = relationship("Vehicle", back_populates="deal_evidence")
