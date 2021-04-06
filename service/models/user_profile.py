from pydantic import BaseModel

class UserProfile(BaseModel):
    role_type: int
