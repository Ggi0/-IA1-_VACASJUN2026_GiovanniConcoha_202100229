from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, TEXT, Enum
from sqlalchemy.sql import func
from app.core.database import Base
import enum


# Enum reutilizado
class InvoiceStatus(enum.Enum):
    PENDING = "PENDING"
    PROCESSED = "PROCESSED"
    ERROR = "ERROR"
    REJECTED = "REJECTED"


class RPAStatus(enum.Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    NOT_EXECUTED = "NOT_EXECUTED"


class ProcessLog(Base):
    __tablename__ = "process_logs"

    id = Column(Integer, primary_key=True, index=True)

    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id"))

    process_date = Column(TIMESTAMP(timezone=True), server_default=func.now())

    status = Column(Enum(InvoiceStatus), nullable=False)
    rpa_result = Column(Enum(RPAStatus))

    message = Column(TEXT)