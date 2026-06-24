from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class HackabilityScore(Base):
    __tablename__ = "hackability_scores"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False, index=True)
    hackability_score = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)
    residual_score = Column(Float, nullable=True)
    incentive_score = Column(Float, nullable=True)
    discount_score = Column(Float, nullable=True)
    inventory_score = Column(Float, nullable=True)
    market_weakness_score = Column(Float, nullable=True)
    evidence_score = Column(Float, nullable=True)
    score_month = Column(Integer, nullable=False)
    score_year = Column(Integer, nullable=False)
    explanation = Column(Text, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow)

    vehicle = relationship("Vehicle", back_populates="hackability_scores")


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id = Column(Integer, primary_key=True, index=True)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String, default="running", nullable=False)
    steps_completed = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
