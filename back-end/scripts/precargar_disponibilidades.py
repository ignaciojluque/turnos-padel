import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import db
from models import Profesor, DisponibilidadProfesor
from datetime import time

def precargar_disponibilidad():
    profesores = Profesor.query.all()

    for profe in profesores:
        print(f"🧩 Asignando franjas a: {profe.nombre}")

        # Ejemplo: lunes (0) 08:00–12:00 y 18:00–21:00
        db.session.add_all([
            DisponibilidadProfesor(profesor_id=profe.id, dia_semana=0, hora_inicio=time(8, 0), hora_fin=time(12, 0)),
            DisponibilidadProfesor(profesor_id=profe.id, dia_semana=0, hora_inicio=time(18, 0), hora_fin=time(21, 0)),

            # Miércoles (2) 10:00–14:00
            DisponibilidadProfesor(profesor_id=profe.id, dia_semana=2, hora_inicio=time(10, 0), hora_fin=time(14, 0)),

            # Viernes (4) 09:00–12:00
            DisponibilidadProfesor(profesor_id=profe.id, dia_semana=4, hora_inicio=time(9, 0), hora_fin=time(12, 0)),
        ])

    db.session.commit()
    print("✅ Disponibilidad asignada correctamente.")
