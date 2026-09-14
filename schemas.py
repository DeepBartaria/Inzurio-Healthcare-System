from pydantic import BaseModel, Field
from typing import List, Optional

class TestResultSchema(BaseModel):
    test_name: str
    value: str
    unit: Optional[str] = None
    reference_range: Optional[str] = None
    confidence: str = Field(description="high, low, or cannot determine")
    is_flagged: str = Field(description="normal, high, low, or critical")

class ReportExtractionSchema(BaseModel):
    report_date: str = Field(description="YYYY-MM-DD")
    results: List[TestResultSchema]
