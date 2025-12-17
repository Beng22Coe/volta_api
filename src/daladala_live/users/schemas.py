from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str  # remove public_id


class UserOut(BaseModel):
    public_id: str  # exposed public id
    email: str
    is_active: bool
