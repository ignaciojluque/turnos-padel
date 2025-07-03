from datetime import datetime, timedelta
from app.models import db, Profesor, Turno, DisponibilidadProfesor, BloqueoAgenda

def generar_turnos(dias=30):
    hoy = datetime.utcnow().date()
    fecha_limite = hoy + timedelta(days=dias)

    profesores = Profesor.query.all()
    bloqueos_raw = BloqueoAgenda.query.all()
    bloqueados = {(b.profesor_id, b.fecha) for b in bloqueos_raw}

    for profe in profesores:
        franjas = DisponibilidadProfesor.query.filter_by(profesor_id=profe.id).all()

        for i in range(dias):
            fecha = hoy + timedelta(days=i)
            if (profe.id, fecha) in bloqueados:
                continue

            dia_semana = fecha.weekday()
            franjas_dia = [f for f in franjas if f.dia_semana == dia_semana]

            for franja in franjas_dia:
                hora = franja.hora_inicio
                while hora < franja.hora_fin:
                    ya_existe = Turno.query.filter_by(
                        profesor_id=profe.id,
                        fecha=fecha,
                        hora=hora
                    ).first()

                    if not ya_existe:
                        nuevo = Turno(
                            profesor_id=profe.id,
                            fecha=fecha,
                            hora=hora,
                            estado="libre"
                        )
                        db.session.add(nuevo)

                    hora_dt = datetime.combine(fecha, hora) + timedelta(hours=1)
                    hora = hora_dt.time()

    db.session.commit()
    print(f"✅ Turnos generados hasta el {fecha_limite}.")
