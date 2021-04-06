from pydantic import BaseModel

class Child(BaseModel):
    id: str
    first_name: str
    last_name: str


class Attendance(BaseModel):
    attended: bool
