import os
import logging
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

# Configuración del contexto de hashing con bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generar_hash_password(password_plano: str) -> str:
    """
    Genera un hash bcrypt de la contraseña en texto plano
    y lo imprime en consola.
    """
    hashed = pwd_context.hash(password_plano)
    logging.info(f"Hash generado: {hashed}")  # imprime en consola con logging
    print(f"Hash generado: {hashed}")         # imprime directo en stdout
    return hashed

def verificar_password(password_plano: str, password_hash: str) -> bool:
    """
    Verifica si la contraseña en texto plano coincide con el hash almacenado.
    """
    return pwd_context.verify(password_plano, password_hash)

if __name__ == "__main__":
    # Ejemplo: encriptar "12345678"
    #Hash generado: $2b$12$BVWrvou.i1zZqvrqEZ4Sr.XTHuXHQnKFjFAixsRLlt.5qWaTB.Cjm
    generar_hash_password("12345678")
