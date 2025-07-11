from datetime import datetime, timedelta
from difflib import SequenceMatcher
import os

def normalizar_monto(monto_raw):
    try:
        return float(str(monto_raw).replace(",", "."))
    except:
        return None

def nombres_similares(nombre_extraido, nombre_esperado, umbral=0.85):
    return SequenceMatcher(None, nombre_extraido.lower(), nombre_esperado.lower()).ratio() >= umbral

def validar_campos_comunes(datos, config, modo_flexible=False):
    errores = []

    nombre = datos.get("destinatario_nombre", "").strip()
    cbu = datos.get("destinatario_cbu")
    monto = normalizar_monto(datos.get("monto"))
    fecha = datos.get("fecha_hora")

    esperado_nombre = config.destinatario
    esperado_cbu = config.cbu
    esperado_monto = config.monto_esperado
    tiempo_maximo = config.tiempo_maximo_minutos

    print("📥 Validando comprobante:")
    print("   - Nombre:", nombre)
    print("   - CBU:", cbu)
    print("   - Monto:", monto)
    print("   - Fecha:", fecha)

    # Validación del nombre con tolerancia a OCR
    if not nombre:
        errores.append("Falta el nombre del destinatario")
    elif not nombres_similares(nombre, esperado_nombre):
        errores.append(f"Nombre del destinatario incorrecto (extraído: '{nombre}')")

    # CBU exacto
    if not cbu:
        errores.append("Falta el CBU")
    elif cbu != esperado_cbu:
        errores.append(f"CBU incorrecto (esperado: {esperado_cbu})")

    # Monto con tolerancia ±0.01
    if monto is None:
        errores.append("Monto no legible o mal formateado")
    elif abs(monto - esperado_monto) > 0.01:
        errores.append(f"Monto incorrecto (esperado: {esperado_monto})")

    # Fecha válida
    if not fecha:
        errores.append("Falta la fecha")
    else:
        if isinstance(fecha, str):
            try:
                fecha = datetime.strptime(fecha, "%d/%m/%Y %H:%M:%S")  # adaptá al formato real de tu parser
            except ValueError:
                errores.append("Formato de fecha inválido")
                fecha = None

        if isinstance(fecha, datetime):
            if not modo_flexible and (datetime.utcnow() - fecha > timedelta(minutes=tiempo_maximo)):
                errores.append("La fecha está fuera del rango permitido")

    es_valido = len(errores) == 0

    print("📋 Resultado validación:")
    print("   - ¿Es válido?", es_valido)
    print("   - Errores:", errores)

    return es_valido, errores
