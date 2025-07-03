from datetime import datetime
import hashlib

def procesar_comprobante_simulado(turno_id: int):
    """
    Simula el procesamiento de un comprobante válido para testing.
    Devuelve: (es_valido, datos extraídos, hash, motivos)
    """
    datos = {
        "monto": 9999,
        "cbu": "1111222233334444555566",
        "nombre": "Tester Dev",
        "fecha_hora": datetime.now(),
        "operacion": f"SIM-{int(datetime.now().timestamp())}"
    }
    huella = hashlib.sha256(f"{turno_id}-{datetime.now()}".encode()).hexdigest()
    return True, datos, huella, []