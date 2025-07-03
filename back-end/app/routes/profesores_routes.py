from flask import Blueprint, jsonify, request, g
from app.models import Profesor, db, DisponibilidadProfesor, Turno, BloqueoAgenda
from app.utils.jwt_utils import jwt_required
from flask_cors import cross_origin
from app.utils.cors_utils import cors_jwt_route
from datetime import datetime, timedelta, time

profesores_bp = Blueprint('profesores', __name__)

@profesores_bp.route('/profesores', methods=['GET'])
def listar_profesores():
    profesores = Profesor.query.order_by(Profesor.nombre).all()

    resultado = []
    for profe in profesores:
        resultado.append({
            "id": profe.id,
            "nombre": profe.nombre,
            "especialidad": profe.especialidad
        })

    return jsonify({"profesores": resultado}), 200

@profesores_bp.route('/administrar-profesores', methods=['POST', 'OPTIONS'])
@cors_jwt_route(methods=["POST"])
def crear_profesor():
    if not g.usuario_actual.es_admin:
        return jsonify({"error": "Solo administradores pueden crear un profesor."}), 403

    data = request.json

    # 1. Crear profesor
    profesor = Profesor(
        nombre=data["nombre"],
        especialidad=data.get("especialidad")
    )
    db.session.add(profesor)
    db.session.flush()

    # 2. Registrar disponibilidades
    disponibilidades = []
    for disponibilidad in data.get("disponibilidades", []):
        try:
            hora_inicio = datetime.strptime(disponibilidad["hora_inicio"], "%H:%M").time()
            hora_fin = datetime.strptime(disponibilidad["hora_fin"], "%H:%M").time()
        except ValueError:
            continue  # Saltar horarios mal formateados

        dispo = DisponibilidadProfesor(
            profesor_id=profesor.id,
            dia_semana=disponibilidad["dia_semana"],
            hora_inicio=hora_inicio,
            hora_fin=hora_fin
        )
        db.session.add(dispo)
        disponibilidades.append(dispo)

    # 3. Registrar bloqueos
    fechas_bloqueadas = set()
    for bloqueo in data.get("bloqueos", []):
        try:
            fecha_bloqueada = datetime.strptime(bloqueo["fecha"], "%Y-%m-%d").date()
        except ValueError:
            continue

        motivo = bloqueo.get("motivo", "")
        bloqueo_entry = BloqueoAgenda(
            profesor_id=profesor.id,
            fecha=fecha_bloqueada,
            motivo=motivo
        )
        db.session.add(bloqueo_entry)
        fechas_bloqueadas.add(fecha_bloqueada)

    # 4. Generar turnos para próximos 30 días
    hoy = datetime.utcnow().date()
    dias_a_generar = 30
    duracion_min = 60
    nuevos_turnos = []

    for i in range(dias_a_generar):
        fecha = hoy + timedelta(days=i)
        if fecha in fechas_bloqueadas:
            continue

        dia_semana = fecha.weekday()

        for dispo in disponibilidades:
            if dispo.dia_semana != dia_semana:
                continue

            hora_inicio = datetime.combine(fecha, dispo.hora_inicio)
            hora_fin = datetime.combine(fecha, dispo.hora_fin)
            actual = hora_inicio

            while actual + timedelta(minutes=duracion_min) <= hora_fin:
                turno = Turno(
                    fecha=fecha,
                    hora=actual.time(),
                    profesor_id=profesor.id,
                    estado="libre"
                )
                db.session.add(turno)
                nuevos_turnos.append(turno)
                actual += timedelta(minutes=duracion_min)

    db.session.commit()

    return jsonify({
        "mensaje": f"✅ Profesor creado con {len(disponibilidades)} disponibilidades, "
                   f"{len(fechas_bloqueadas)} bloqueos y {len(nuevos_turnos)} turnos generados."
    }), 201

@profesores_bp.route('/administrar-profesores/<int:profesor_id>', methods=['DELETE'])
@cors_jwt_route(methods=["DELETE"])
def borrar_profesor(profesor_id):
    if not g.usuario_actual.es_admin:
        return jsonify({"error": "Solo administradores pueden borrar profesores."}), 403

    profesor = Profesor.query.get(profesor_id)
    if not profesor:
        return jsonify({"error": "Profesor no encontrado."}), 404

    Turno.query.filter_by(profesor_id=profesor.id).delete()
    DisponibilidadProfesor.query.filter_by(profesor_id=profesor.id).delete()
    BloqueoAgenda.query.filter_by(profesor_id=profesor.id).delete()
    db.session.delete(profesor)
    db.session.commit()

    return jsonify({"mensaje": f"🗑️ Profesor {profesor.nombre} eliminado correctamente."}), 200
