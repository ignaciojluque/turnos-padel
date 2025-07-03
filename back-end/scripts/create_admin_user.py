import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import db, app
from models import Usuario
from werkzeug.security import generate_password_hash

with app.app_context():
    admin = Usuario(
        nombre="Administrador",
        email="admin@ejemplo.com",
        telefono="123456789",
        password=generate_password_hash("admin123"),
        es_admin=True
    )
    db.session.add(admin)
    db.session.commit()
    print("✅ Usuario administrador creado con éxito.")
