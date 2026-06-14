from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.db import get_db
from app.service.auth_service import AuthService
from app.schemas.auth_schema import LoginRequest

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    return AuthService.login(
        db,
        data.usuario,
        data.password
    )