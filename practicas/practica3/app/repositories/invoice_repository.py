from sqlalchemy.orm import Session
from app.models.invoice_model import Invoice, InvoiceStatus


class InvoiceRepository:

    def get_all(self, db: Session):
        return db.query(Invoice).all()

    def get_by_id(self, db: Session, invoice_id: int):
        return db.query(Invoice).filter(Invoice.id == invoice_id).first()

    # DETECCIÓN DE DUPLICADOS
    def find_duplicate(self, db: Session, invoice_number: str, nit: str):
        return db.query(Invoice).filter(
            Invoice.invoice_number == invoice_number,
            Invoice.nit == nit
        ).first()

    # CREACIÓN (usada por RPA)
    def create(self, db: Session, data: dict):
        invoice = Invoice(**data)
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        return invoice

    # ✅ CREAR CON VALIDACIÓN DE DUPLICADO
    def create_with_duplicate_check(self, db: Session, data: dict):
        duplicate = self.find_duplicate(
            db,
            data["invoice_number"],
            data["nit"]
        )

        if duplicate:
            data["is_duplicate"] = True

        invoice = Invoice(**data)
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        return invoice

    def update_status(self, db: Session, invoice_id: int, status: InvoiceStatus):
        invoice = self.get_by_id(db, invoice_id)

        if invoice:
            invoice.status = status
            db.commit()
            db.refresh(invoice)

        return invoice