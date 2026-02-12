from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from forum.schemas import Pagination


class UserBase(BaseModel):
    """Base Pydantic model for User."""

    username: str

    # Allows conversion from SQLAlchemy to Pydantic Model
    model_config = ConfigDict(from_attributes=True)


class UserLogin(UserBase):
    """Pydantic model for User login."""

    password: str


class UserLoginResponse(BaseModel):
    """Pydantic model for the response when User login."""

    token: "Token"


class UserCreate(UserBase):
    """Pydantic model for User creation."""

    email: EmailStr
    username: str
    password: str


class UserCreateResponse(BaseModel):
    """Pydantic model for the response after User is created."""

    token: str


class UserRead(UserBase):
    email: EmailStr
    created_at: datetime


class UserPagination(Pagination):
    """Pydantic model for paginated results of Users."""

    items: list[UserRead]


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
