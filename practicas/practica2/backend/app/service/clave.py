from passlib.context import CryptContext

# Configuración del contexto de hashing con bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generar_hash_password(password_plano: str) -> str:
    """
    Genera un hash bcrypt de la contraseña en texto plano
    y lo imprime en consola.
    """
    hashed = pwd_context.hash(password_plano)
    print(f"Hash generado: {hashed}")
    return hashed

if __name__ == "__main__":
    # Ejemplo: encriptar "admin123"
    generar_hash_password("admin123")
