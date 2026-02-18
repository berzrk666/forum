from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

import jwt
from argon2 import PasswordHasher
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Integer, LargeBinary, String

from forum.auth.schemas import TokenData
from forum.config import settings
from forum.database.core import Base, TimestampMixin

if TYPE_CHECKING:
    from forum.thread.models import Thread


def hash_password(password: str) -> bytes:
    """Hash a password using argon2."""
    hash = PasswordHasher().hash(password)
    return hash.encode("utf-8")


def verify_hash(password: str, hash: bytes) -> bool:
    """Check if password matches the hash."""
    return PasswordHasher().verify(hash, password)


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    password: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    # Relationships
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=True)
    role: Mapped["Role"] = relationship(back_populates="users")

    threads: Mapped[list["Thread"]] = relationship(back_populates="author")

    def verify_password(self, password: str) -> bool:
        """Check if the `password` matches the hashed password in database."""
        if not password:
            raise ValueError("Password cannot be empty")
        return verify_hash(password, self.password)

    def set_password(self, password: str):
        """Set a new password for the User."""
        if not password:
            raise ValueError("Password cannot be empty")
        self.password = hash_password(password)

    @property
    def token(self) -> str:
        """Generate a JWT Token for the User."""
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRATION)
        to_encode = TokenData(sub=self.username, exp=expire, role=self.role.name)
        return jwt.encode(to_encode.model_dump(), settings.JWT_KEY, settings.JWT_ALG)

    def __repr__(self) -> str:
        return f"User=(id={self.id!r}, username={self.username!r}, created_at={self.created_at!r}, updated_at={self.updated_at!r})"


class Role(Base):
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)

    users: Mapped[list[User]] = relationship(back_populates="role")
