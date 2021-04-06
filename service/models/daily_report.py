from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class DailyReport:
    record_id: int
    sender_id: int
    child_id: str
    report_date: datetime
    category_id: int
    subcategory_id: int
    report_value: str
    def __init__(self, record_id: int, sender_id: int, child_id: str, report_date: datetime, category_id: int, subcategory_id: int, report_value: str):
        self.record_id = record_id
        self.sender_id = sender_id
        self.child_id = child_id
        self.report_date = report_date
        self.category_id = category_id
        self.subcategory_id = subcategory_id
        self.report_value = report_value

class DailyReportAddDto(BaseModel):
    value: str
    category_id: Optional[int]
    subcategory_id: Optional[int]


class DailyReportGetDto(DailyReportAddDto):
    sender_id: int
    timestamp: str
