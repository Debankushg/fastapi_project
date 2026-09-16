from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, model_validator


class UserRegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    address: str = Field(min_length=1, max_length=500)
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)

    @model_validator(mode="after")
    def passwords_match(self) -> "UserRegisterRequest":
        if self.password != self.confirm_password:
            raise ValueError("password and confirm_password do not match")
        return self


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    address: str
    is_active: bool
    profile_image: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    address: str | None = Field(default=None, min_length=1, max_length=500)

    @model_validator(mode="after")
    def at_least_one_field(self) -> "UserUpdateRequest":
        if self.name is None and self.address is None:
            raise ValueError("Provide at least one field to update (name or address)")
        return self
