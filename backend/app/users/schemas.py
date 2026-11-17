from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints

from app.users.models import UserRole

UserName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=2, max_length=120),
]


class UserCreate(BaseModel):
    name: UserName
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserUpdate(BaseModel):
    name: UserName
    email: EmailStr
    password: str | None = Field(
        default=None,
        min_length=8,
        max_length=128,
    )


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime
