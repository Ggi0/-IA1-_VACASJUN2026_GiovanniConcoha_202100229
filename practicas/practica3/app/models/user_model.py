from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, Enum
from sqlalchemy.sql import func
from app.core.database import Base
import enum


# Enum para roles
class UserRole(enum.Enum):
    ADMIN = "ADMIN"
    EMPLOYEE = "EMPLOYEE"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

    role = Column(Enum(UserRole), default=UserRole.EMPLOYEE, nullable=False)

    is_active = Column(Boolean, default=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())