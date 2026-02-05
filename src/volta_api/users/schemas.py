from pydantic import BaseModel, EmailStr, Field, model_validator
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    MODERATOR = "moderator"
    DRIVER = "driver"


class UserCreate(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(..., min_length=8)
    password_confirm: str = Field(..., min_length=8)
    role: UserRole = UserRole.DRIVER

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")
        return self


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=120)
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserOut(BaseModel):
    public_id: str
    full_name: Optional[str] = None
    email: str
    role: str
    is_active: bool
    is_email_verified: Optional[bool] = False
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserListOut(BaseModel):
    items: list[UserOut]
    total: int
    page: int
    page_size: int
    total_pages: int


class UserDeleteConfirm(BaseModel):
    confirm: str = Field(..., min_length=1)
