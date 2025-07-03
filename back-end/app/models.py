# models.py
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefono = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    turnos = db.relationship('Turno', backref='usuario')
    es_admin = db.Column(db.Boolean, default=False) 
    modo_test = db.Column(db.Boolean, default=False)


class Profesor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    especialidad = db.Column(db.String(100))
    turnos = db.relationship('Turno', backref='profesor')

class Turno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    estado = db.Column(db.String(20), default='disponible')  # o 'pendiente', 'confirmado'
    profesor_id = db.Column(db.Integer, db.ForeignKey('profesor.id'))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    external_reference = db.Column(db.String(100), unique=True)
    comprobante_url = db.Column(db.String)
    reservado_temporalmente = db.Column(db.Boolean, default=False)
    tiempo_expiracion = db.Column(db.DateTime)
    estado_pago = db.Column(db.String(20), default="pendiente")
    fecha_expiracion = db.Column(db.DateTime)

class Pago(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    external_reference = db.Column(db.String(100), unique=True)
    estado = db.Column(db.String(50))
    monto = db.Column(db.Float)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    fecha = db.Column(db.DateTime)
    cbu = db.Column(db.String(64))


class RefreshToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token_hash = db.Column(db.String(255), nullable=False, unique=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    expira_en = db.Column(db.DateTime, nullable=False)
    revocado = db.Column(db.Boolean, default=False)

    def verificar_token(self, token_claro):
        return check_password_hash(self.token_hash, token_claro)

class Comprobante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    turno_id = db.Column(db.Integer, db.ForeignKey('turno.id'), nullable=False)
    hash_archivo = db.Column(db.String(64), unique=True, nullable=False)
    nro_operacion = db.Column(db.String(32), nullable=True)
    fecha_detectada = db.Column(db.DateTime, nullable=True)
    valido = db.Column(db.Boolean, default=False)
    timestamp_carga = db.Column(db.DateTime, default=datetime.utcnow)
    emisor_nombre = db.Column(db.String(100))
    emisor_cbu = db.Column(db.String(30))
    emisor_cuit = db.Column(db.String(20))
    archivo_blob = db.Column(db.LargeBinary, nullable=True)
    mimetype = db.Column(db.String(100), nullable=True)
    nombre_archivo = db.Column(db.String(255), nullable=True)

    turno = db.relationship('Turno', backref=db.backref('comprobante_detalle', uselist=False))

class DisponibilidadProfesor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profesor_id = db.Column(db.Integer, db.ForeignKey('profesor.id'), nullable=False)
    dia_semana = db.Column(db.Integer, nullable=False)  # 0 = lunes, 6 = domingo
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)

    profesor = db.relationship('Profesor', backref=db.backref('disponibilidades', lazy=True))

class BloqueoAgenda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profesor_id = db.Column(db.Integer, db.ForeignKey('profesor.id'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    motivo = db.Column(db.String(100))

    profesor = db.relationship('Profesor', backref=db.backref('bloqueos', lazy=True))

class ConfiguracionPago(db.Model):
    __tablename__ = "configuracion_pago"
    id = db.Column(db.Integer, primary_key=True)
    destinatario = db.Column(db.String(255))
    cbu = db.Column(db.String(64))
    monto_esperado = db.Column(db.Float)
    tiempo_maximo_minutos = db.Column(db.Integer)
