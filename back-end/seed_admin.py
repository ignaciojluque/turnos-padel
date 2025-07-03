# back-end/seed_admin.py

from app import create_app, db
from app.models import Usuario, ConfiguracionPago
from sqlalchemy.exc import IntegrityError
from sqlalchemy import inspect
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    print("📍 Base conectada a:", db.engine.url)

    # 👤 Crear usuario admin
    admin_email = "admin@admin.com"
    if not Usuario.query.filter_by(email=admin_email).first():
        print("👤 Creando usuario admin por defecto...")
        admin = Usuario(
            nombre="Administrador",
            telefono="12345678",
            email=admin_email,
            password=generate_password_hash("admin"),
            es_admin=True
        )
        db.session.add(admin)
        try:
            db.session.commit()
            print("✅ Usuario admin creado.")
        except IntegrityError:
            db.session.rollback()
            print("⚠️ Ya existe un admin con ese email.")
    else:
        print("ℹ️ Usuario admin ya existe.")

    # 💰 Crear configuración de pago por defecto (si la tabla existe)
    inspector = inspect(db.engine)
    if "configuracion_pago" in inspector.get_table_names():
        if not ConfiguracionPago.query.first():
            print("💸 Insertando configuración de pago por defecto...")
            config = ConfiguracionPago(
                destinatario="CHANGEIT",
                cbu="000000000000CHANGEIT",
                monto_esperado=0.0,
                tiempo_maximo_minutos=30
            )
            db.session.add(config)
            try:
                db.session.commit()
                print("✅ Configuración de pago inicial creada.")
            except IntegrityError:
                db.session.rollback()
                print("⚠️ Falló la inserción de configuración de pago.")
        else:
            config = ConfiguracionPago.query.first()
            print("ℹ️ Configuración ya existente:")
            print(f"   🧾 Destinatario: {config.destinatario}")
            print(f"   🧾 CBU: {config.cbu}")
            print(f"   💵 Monto esperado: {config.monto_esperado}")
            print(f"   ⏱️ Tiempo máximo: {config.tiempo_maximo_minutos} minutos")
    else:
        print("⛔ Tabla 'configuracion_pago' no encontrada. Saltando seed de configuración.")
