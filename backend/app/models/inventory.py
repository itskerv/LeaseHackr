from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class InventoryMetric(Base):
    __tablename__ = "inventory_metrics"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False, index=True)
    region = Column(String, default="National")
    inventory_count = Column(Integer, nullable=True)
    avg_days_on_market = Column(Float, nullable=True)
    price_reduction_count = Column(Integer, nullable=True)
    dealer_count = Column(Integer, nullable=True)
    recorded_date = Column(Date, nullable=False)
    source = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    vehicle = relationship("Vehicle", back_populates="inventory_metrics")
