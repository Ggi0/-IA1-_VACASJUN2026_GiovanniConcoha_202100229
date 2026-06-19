from sqlalchemy import Column, Integer, String, Numeric, Boolean, ForeignKey, Date, TIMESTAMP, Enum
from sqlalchemy.sql import func
from app.core.database import Base
import enum


# Enum para estado de factura
class InvoiceStatus(enum.Enum):
    PENDING = "PENDING"
    PROCESSED = "PROCESSED"
    ERROR = "ERROR"
    REJECTED = "REJECTED"


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    provider_id = Column(Integer, ForeignKey("providers.id"))

    invoice_number = Column(String(50), nullable=False)
    date = Column(Date)

    nit = Column(String(20))

    subtotal = Column(Numeric(10, 2))
    taxes = Column(Numeric(10, 2))
    total = Column(Numeric(10, 2))

    file_path = Column(String, nullable=False)

    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.PENDING)

    is_duplicate = Column(Boolean, default=False)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())