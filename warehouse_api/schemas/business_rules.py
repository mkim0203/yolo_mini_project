
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal
from datetime import datetime


class BusinessRuleCreate(BaseModel):
    rule_name: str = Field(..., max_length=100)
    category: str = Field(..., max_length=30)
    target_tables: Optional[list[str]] = None
    rule_content: Optional[str] = Field(None, max_length=1024)


class BusinessRuleStatusUpdate(BaseModel):
    status: Literal["pending", "approved", "rejected"]


class BusinessRuleActiveUpdate(BaseModel):
    is_active: Literal["Y", "N"]


class BusinessRuleResponse(BaseModel):
    rule_id: int
    rule_name: str
    category: str
    target_tables: Optional[list[str]]
    rule_content: Optional[str]
    status: Optional[str]
    is_active: str
    create_date: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)
