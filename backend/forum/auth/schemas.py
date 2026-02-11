from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    """Base Pydantic model for User."""

    email: EmailStr

    # Allows conversion from SQLAlchemy to Pydantic Model
    model_config = ConfigDict(from_attributes=True)


class UserLogin(UserBase):
    """Pydantic model for User login."""

    password: str


class UserCreate(UserBase):
    """Pydantic model for User creation."""

    password: str
