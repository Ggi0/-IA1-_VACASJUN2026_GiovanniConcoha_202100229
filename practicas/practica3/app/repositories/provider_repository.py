from sqlalchemy.orm import Session
from app.models.provider_model import Provider


class ProviderRepository:

    def get_all(self, db: Session):
        return db.query(Provider).all()

    def get_by_id(self, db: Session, provider_id: int):
        return db.query(Provider).filter(Provider.id == provider_id).first()

    def get_by_nit(self, db: Session, nit: str):
        return db.query(Provider).filter(Provider.nit == nit).first()

    def create(self, db: Session, data: dict):
        provider = Provider(**data)
        db.add(provider)
        db.commit()
        db.refresh(provider)
        return provider

    def update(self, db: Session, provider: Provider, data: dict):
        for key, value in data.items():
            setattr(provider, key, value)

        db.commit()
        db.refresh(provider)
        return provider

    def delete(self, db: Session, provider: Provider):
        db.delete(provider)
        db.commit()

    # IMPORTANTE para RPA
    def get_or_create_by_nit(self, db: Session, name: str, nit: str):
        provider = self.get_by_nit(db, nit)

        if provider:
            return provider

        provider = Provider(name=name, nit=nit)
        db.add(provider)
        db.commit()
        db.refresh(provider)
        return provider