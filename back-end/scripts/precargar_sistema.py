import sys
import os
from datetime import time, date
from werkzeug.security import generate_password_hash

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import app
from app.models import db, Profesor, DisponibilidadProfesor, BloqueoAgenda, Usuario
from scripts.generar_turnos import generar_turnos

def run():
    with app.app_context():
        # 1. Profesores base (solo si no hay ninguno)
        if not Profesor.query.first():
            print("🧑‍🏫 Cargando profesores...")
            profe1 = Profesor(nombre="Ana Fernández", especialidad="Táctica ofensiva")
            profe2 = Profesor(nombre="Luciano Gómez", especialidad="Técnica y control")
            profe3 = Profesor(nombre="Sofía Martínez", especialidad="Defensa y volea")
            db.session.add_all([profe1, profe2, profe3])
            db.session.commit()

            # Disponibilidad semanal
            print("📅 Cargando disponibilidad semanal...")
            franjas = [
                DisponibilidadProfesor(profesor_id=profe1.id, dia_semana=0, hora_inicio=time(8, 0), hora_fin=time(12, 0)),
                DisponibilidadProfesor(profesor_id=profe1.id, dia_semana=0, hora_inicio=time(18, 0), hora_fin=time(21, 0)),
                DisponibilidadProfesor(profesor_id=profe1.id, dia_semana=2, hora_inicio=time(10, 0), hora_fin=time(14, 0)),
                DisponibilidadProfesor(profesor_id=profe2.id, dia_semana=1, hora_inicio=time(9, 0), hora_fin=time(12, 0)),
                DisponibilidadProfesor(profesor_id=profe2.id, dia_semana=3, hora_inicio=time(17, 0), hora_fin=time(21, 0)),
                DisponibilidadProfesor(profesor_id=profe3.id, dia_semana=4, hora_inicio=time(8, 0), hora_fin=time(11, 0)),
                DisponibilidadProfesor(profesor_id=profe3.id, dia_semana=4, hora_inicio=time(15, 0), hora_fin=time(18, 0)),
            ]
            db.session.add_all(franjas)

            print("🚫 Agregando bloqueo por vacaciones...")
            db.session.add(BloqueoAgenda(profesor_id=profe1.id, fecha=date(2025, 7, 15), motivo="Vacaciones"))
            db.session.commit()

        else:
            print("✅ Profesores ya existen — omitiendo carga.")

        # 2. Usuarios base
        print("👤 Cargando usuarios base...")
        if not Usuario.query.filter_by(email="nacho@example.com").first():
            nacho = Usuario(
              nombre="Nacho",
              email="nacho@example.com",
              telefono="1234567890",
              password=generate_password_hash("nacho"),
              es_admin=False
          )

            db.session.add(nacho)

        if not Usuario.query.filter_by(email="admin@example.com").first():
            admin = Usuario(
                nombre="Administrador",
                email="admin@example.com",
                telefono="0000000000",
                password=generate_password_hash("admin"),
                es_admin=True
            )
            db.session.add(admin)

        db.session.commit()

        # 3. Turnos
        print("⏳ Generando turnos disponibles...")
        generar_turnos(30)

        print("✅ Sistema precargado exitosamente.")

if __name__ == "__main__":
    run()
