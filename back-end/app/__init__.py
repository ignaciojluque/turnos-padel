import logging
import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

from app import models

from app.models import db  # importa solo la instancia, no todo con *
from app.routes.auth_routes import auth_bp
from app.routes.turnos_routes import turnos_bp
from app.routes.profesores_routes import profesores_bp
from app.routes.pagos_routes import pagos_bp
from app.routes.usuarios_routes import usuarios_bp
from config import DevelopmentConfig, ProductionConfig
from flask import request
from app.extensiones import mail


load_dotenv()  # carga el .env desde la raíz del proyecto



def create_app():
    app = Flask(__name__)

    # Detectar entorno
    env = os.getenv("FLASK_ENV", "development")

    if env == "production":
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)   

    # Inicializar extensiones
    db.init_app(app)
    Migrate(app, db)
    origins = app.config["API_ORIGINS"]
    if isinstance(origins, str):
        origins = [o.strip() for o in origins.split(",")]


    # Configuración de Flask-Mail desde variables de entorno
    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER")
    app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 465))
    app.config["MAIL_USE_SSL"] = os.getenv("MAIL_USE_SSL", "true").lower() == "true"
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
    app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER")

    mail.init_app(app)


    CORS(app, origins=origins, supports_credentials=True)

    print("📍 Base conectada a:", app.config["SQLALCHEMY_DATABASE_URI"])

    # Registrar Blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(turnos_bp, url_prefix="/turnos")
    app.register_blueprint(profesores_bp)
    app.register_blueprint(pagos_bp)
    app.register_blueprint(usuarios_bp)
    with app.app_context():
        from . import models  # ← ¡Este import garantiza que Alembic vea los modelos!

    return app


# Para uso con Flask CLI: flask --app app:create_app run
def get_app():
    return app

app = create_app()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(debug=True)