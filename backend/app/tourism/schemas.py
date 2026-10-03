from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TourismEstablishmentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    category: str = Field(min_length=1, max_length=100)


class TourismEstablishmentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    category: str | None = Field(default=None, min_length=1, max_length=100)
    is_active: bool | None = None


class TourismEstablishmentResponse(BaseModel):
    id: int
    name: str
    category: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
