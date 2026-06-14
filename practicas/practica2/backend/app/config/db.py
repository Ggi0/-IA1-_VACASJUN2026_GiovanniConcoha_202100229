from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy import text

import os


load_dotenv()


DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


DATABASE_URL = (
    f"postgresql://"
    f"{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}"
    f"/{DB_NAME}"
)


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)


def verificar_conexion():
    """
    Verifica si PostgreSQL responde correctamente.
    """

    try:

        with engine.connect() as connection:

            connection.execute(
                text("SELECT 1")
            )

            print(
                "[DATABASE] Conexión correcta con PostgreSQL."
            )

            return True

    except Exception as e:

        print(
            "[DATABASE] Error de conexión a PostgreSQL:"
        )

        print(e)

        return False