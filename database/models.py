from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Inspection(Base):
    __tablename__ = 'inspections'
    id = Column(String, primary_key=True)
    company_name = Column(String)
    operator_name = Column(String)
    roll_id = Column(String)
    batch_id = Column(String)
    fabric_type = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    quality_score = Column(Float)
    final_verdict = Column(String) # PASS, REWORK, REJECT
    inspector_remarks = Column(Text, nullable=True)
    report_path = Column(String, nullable=True)
    annotated_image_path = Column(String, nullable=True)
    
    defects = relationship("Defect", back_populates="inspection")

class Defect(Base):
    __tablename__ = 'defects'
    id = Column(Integer, primary_key=True, autoincrement=True)
    inspection_id = Column(String, ForeignKey('inspections.id'))
    defect_type = Column(String) # Hole, Tear, Stain
    confidence = Column(Float)
    x_center = Column(Float)
    y_center = Column(Float)
    width_cm = Column(Float)
    height_cm = Column(Float)
    area_cm2 = Column(Float)
    severity = Column(String) # Minor, Moderate, Critical
    suggestion = Column(String)
    
    inspection = relationship("Inspection", back_populates="defects")
