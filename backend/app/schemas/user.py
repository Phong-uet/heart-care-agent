import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    full_name: str = Field(min_length=1, max_length=255)


class UserLogin(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    full_name: str
    role: UserRole


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"