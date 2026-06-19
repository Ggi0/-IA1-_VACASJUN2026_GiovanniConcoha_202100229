from sqlalchemy.orm import Session

from app.models.consulta import Consulta


class ConsultaRepository:

    @staticmethod
    def registrar(
        db: Session,
        chat_id: int,
        pregunta: str,
        respuesta: str = None
    ):

        consulta = Consulta(
            chat_id=chat_id,
            pregunta_realizada=pregunta,
            respuesta_entregada=respuesta
        )

        db.add(consulta)

        db.commit()

        db.refresh(consulta)

        return consulta
    
    @staticmethod
    def listar(
        db: Session
    ):

        return (
            db.query(Consulta)
            .order_by(
                Consulta.fecha_consulta.desc()
            )
            .all()
        )