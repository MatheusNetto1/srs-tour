from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.reports.models import ReportStatus


class ReportCreate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    description: str | None = Field(default=None, max_length=5000)
    category: str = Field(min_length=2, max_length=100)
    year: int = Field(ge=1900, le=2100)


class ReportUpdate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    description: str | None = Field(default=None, max_length=5000)
    category: str = Field(min_length=2, max_length=100)
    year: int = Field(ge=1900, le=2100)


class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    category: str
    year: int
    status: ReportStatus
    published_at: datetime | None
    file_path: str | None
    created_at: datetime
    updated_at: datetime
