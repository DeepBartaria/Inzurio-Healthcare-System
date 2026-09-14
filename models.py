from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
import datetime

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    report_date = Column(String, index=True) # Storing as YYYY-MM-DD string for simplicity
    file_path = Column(String)
    raw_text = Column(String)
    
    results = relationship("TestResult", back_populates="report")

class TestResult(Base):
    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"))
    test_name = Column(String, index=True)
    value = Column(String) # Storing and will parse to float when needed
    unit = Column(String)
    reference_range = Column(String)
    confidence = Column(String) # "high", "low", "cannot determine"
    is_flagged = Column(String) # "normal", "high", "low", "critical"

    report = relationship("Report", back_populates="results")
