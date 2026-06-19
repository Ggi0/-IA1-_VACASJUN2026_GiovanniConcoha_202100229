from sqlalchemy import Column, Integer, String, TEXT, TIMESTAMP
from sqlalchemy.sql import func
from app.core.database import Base


class Provider(Base):
    __tablename__ = "providers"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(150), nullable=False)
    nit = Column(String(20), unique=True, nullable=False)

    address = Column(TEXT)
    phone = Column(String(20))

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
