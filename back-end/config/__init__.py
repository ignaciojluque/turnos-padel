import os
from dotenv import load_dotenv

load_dotenv()  # Carga automática de .env

class BaseConfig:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MERCADO_PAGO_TOKEN = os.getenv('MERCADO_PAGO_TOKEN')
    TURNO_EXPIRA_MINUTOS = int(os.getenv('TURNO_EXPIRA_MINUTOS', 15))
    API_ORIGINS = os.getenv("API_ORIGINS", "http://localhost:5173")

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///instance/turnos.db")
    APROBAR_COMPROBANTE = os.getenv("APROBAR_COMPROBANTE", "false").lower() == "true"


class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")  # En prod es obligatorio
