# pylint: disable=no-name-in-module
from pydantic import BaseModel, validator


class KesherDto(BaseModel):
    name: str

    # pylint: disable=no-self-argument,no-self-use,invalid-name
    @validator('name')
    def validate_changes(cls, v):
        if not v:
            raise ValueError('name cannot be empty')
        return v
