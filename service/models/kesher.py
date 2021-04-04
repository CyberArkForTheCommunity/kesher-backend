# pylint: disable=no-name-in-module
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, validator


class Kesher(BaseModel):
    name: str
    created_date: Optional[Decimal]
    updated_date: Optional[Decimal]

    # pylint: disable=no-self-argument,no-self-use,invalid-name
    @validator('name')
    def validate_changes(cls, v):
        if not v:
            raise ValueError('name cannot be empty')
        return v
