from sqlalchemy.orm import Session

from app.models.usuario import Usuario


class UsuarioRepository:

    @staticmethod
    def obtener_por_usuario(
        db: Session,
        usuario: str
    ):

        return (
            db.query(Usuario)
            .filter(
                Usuario.usuario == usuario
            )
            .first()
        )

    @staticmethod
    def obtener_por_id(
        db: Session,
        usuario_id: int
    ):

        return (
            db.query(Usuario)
            .filter(
                Usuario.id == usuario_id
            )
            .first()
        )