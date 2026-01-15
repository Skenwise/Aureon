# models/misc/currency.py
from sqlmodel import SQLModel, Field
from ..base import BaseModel

class Currency(BaseModel, table=True):
    """
    Represents currencies supported by the system
    """
    code: str = Field(..., max_length=3, unique=True, index=True)  # ISO code
    name: str = Field(..., max_length=50)
    decimals: int = Field(default=2)  # number of decimal places