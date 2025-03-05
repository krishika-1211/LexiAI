from datetime import datetime, timedelta
from enum import Enum

import jwt
from passlib.hash import pbkdf2_sha256
from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Boolean, String

from src.config import Config
from src.conversation.models import ConversationSession
from utils.db.base import ModelBase


class UserRoles(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class AuthProvider(Enum):
    GOOGLE = "google"


class User(ModelBase):
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    email_verified = Column(Boolean, default=False)
    password = Column(String, nullable=False)
    role = Column(String, default=UserRoles.USER.value)
    is_active = Column(Boolean, default=True)
    is_banned = Column(Boolean, default=False)

    session = relationship(
        ConversationSession, back_populates="user", cascade="all, delete"
    )

    def __repr__(self):
        return f"""
            User INFO:
                ID: {self.id}
                First name: {self.first_name}
                Last name: {self.last_name}
                Email: {self.email}
                role: {self.role}
        """

    def set_password(self, password):
        """Hash a password for storing."""
        self.password = pbkdf2_sha256.hash(password)

    def verify_password(self, provided_password):
        """Verify a stored password against one provided by user"""
        return pbkdf2_sha256.verify(provided_password, self.password)

    def create_token(self):
        return jwt.encode(
            {
                "id": self.id,
                "email": self.email,
                "role": self.role,
                "is_active": self.is_active,
                "is_banned": self.is_banned,
                "exp": (
                    datetime.utcnow()
                    + timedelta(seconds=int(Config.JWT_EXPIRATION_TIME))
                ).timestamp(),
            },
            key=Config.JWT_SECRET_KEY,
            algorithm=Config.JWT_ALGORITHM,
        )
