from datetime import datetime

def parsear_fecha_hora(fecha_str):
    try:
        return datetime.strptime(fecha_str, "%d/%m/%Y %H:%M:%S")
    except ValueError:
        return None  # o lanzar una excepción si querés forzar validación
