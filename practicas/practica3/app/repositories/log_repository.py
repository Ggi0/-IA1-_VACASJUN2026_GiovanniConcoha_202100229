from sqlalchemy.orm import Session
from app.models.log_model import ProcessLog, InvoiceStatus, RPAStatus


class LogRepository:

    def create_log(
        self,
        db: Session,
        invoice_id: int,
        user_id: int,
        status: InvoiceStatus,
        rpa_result: RPAStatus,
        message: str
    ):
        log = ProcessLog(
            invoice_id=invoice_id,
            user_id=user_id,
            status=status,
            rpa_result=rpa_result,
            message=message
        )

        db.add(log)
        db.commit()
        db.refresh(log)

        return log

    def get_logs_by_invoice(self, db: Session, invoice_id: int):
        return db.query(ProcessLog).filter(
            ProcessLog.invoice_id == invoice_id
        ).all()

    def get_all_logs(self, db: Session):
        return db.query(ProcessLog).all()
