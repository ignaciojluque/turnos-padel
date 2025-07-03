from app.models import db

def revertir_turno(turno):
    turno.estado = "libre"
    turno.estado_pago = "pendiente"
    turno.fecha_expiracion = None
    db.session.commit()