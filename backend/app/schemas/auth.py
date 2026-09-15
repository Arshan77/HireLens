from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator


class UserRegisterRequest(BaseModel):
    email: EmailStr = Field(..., description="User registration email address")
    password: str = Field(..., min_length=6, description="Password (min 6 characters)")

    @field_validator("password")
    @classmethod
    def validate_password_byte_length(cls, v: str) -> str:
        pwd_bytes = v.encode("utf-8")
        if len(pwd_bytes) > 72:
            raise ValueError("Password cannot exceed 72 UTF-8 bytes.")
        return v


class UserLoginRequest(BaseModel):
    email: str = Field(..., description="Registered email address")
    password: str = Field(..., description="User password")


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT Bearer access token")
    token_type: str = Field(default="bearer", description="Token type")


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique user ID")
    email: str = Field(..., description="User email address")
    is_active: bool = Field(..., description="Account active status")
    created_at: datetime = Field(..., description="Registration timestamp")
