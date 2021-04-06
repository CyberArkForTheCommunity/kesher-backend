from typing import Optional
from pydantic import BaseModel


class DailyReportAdd(BaseModel):
    value: str
    category_id: Optional[int]
    subcategory_id: Optional[int]


class DailyReportGet(DailyReportAdd):
    sender_id: int
    timestamp: int
