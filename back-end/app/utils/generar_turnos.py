from datetime import datetime, timedelta, time
from app.models import db, Profesor, DisponibilidadProfesor, Turno

def generar_turnos_proximos_dias(dias=30):
    hoy = datetime.utcnow().date()
    profesores = Profesor.query.all()

    for profesor in profesores:
        disponibilidades = DisponibilidadProfesor.query.filter_by(profesor_id=profesor.id).all()

        for i in range(dias):
            fecha = hoy + timedelta(days=i)
            dia_semana = fecha.weekday()  # 0 = lunes, 6 = domingo

            franjas_del_dia = [f for f in disponibilidades if f.dia_semana == dia_semana]

            for franja in franjas_del_dia:
                hora_actual = franja.hora_inicio
                while hora_actual < franja.hora_fin:
                    ya_existe = Turno.query.filter_by(
                        profesor_id=profesor.id,
                        fecha=fecha,
                        hora=hora_actual
                    ).first()

                    if not ya_existe:
                        nuevo = Turno(
                            profesor_id=profesor.id,
                            fecha=fecha,
                            hora=hora_actual,
                            estado="libre"
                        )
                        db.session.add(nuevo)

                    # Paso de 1 hora (ajustá si querés slots de 30 min)
                    dt = datetime.combine(fecha, hora_actual) + timedelta(hours=1)
                    hora_actual = dt.time()

    db.session.commit()
    print(f"✅ Turnos generados hasta el {hoy + timedelta(days=dias)}.")
