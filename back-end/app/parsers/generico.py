import re
from datetime import datetime

def extraer_datos(texto):
    print("🧾 [GENERICO] Ejecutando extracción GENERICA")  

    datos = {}

    # Buscar CBU (último de 22 dígitos)
    cbu_matches = re.findall(r"\b\d{22}\b", texto)
    if cbu_matches:
        datos["destinatario_cbu"] = cbu_matches[-1]

    # Buscar monto
    monto = re.search(r"\$\s*([0-9.,]+)", texto)
    if monto:
        datos["monto"] = monto.group(1).replace(",", ".").strip()

    # Buscar fecha y hora
    fecha = re.search(r"(\d{2}/\d{2}/\d{4})|(\d{1,2} de \w+ de \d{4})", texto)
    hora = re.search(r"\b(\d{1,2}:\d{2})\b", texto)
    fecha_hora = None
    try:
        if fecha and hora:
            fecha_str = fecha.group(0).replace("/", "-").replace(" de ", " ")
            fecha_hora = datetime.strptime(f"{fecha_str} {hora.group(1)}", "%d-%m-%Y %H:%M")
    except:
        pass
    datos["fecha_hora"] = fecha_hora

    # Buscar nombre del destinatario
    nombre = re.search(r"(?:Beneficiario|Destinatario)[:\s]*\n*([^\n]+)", texto, re.IGNORECASE)
    if nombre:
        datos["destinatario_nombre"] = nombre.group(1).strip()

    # Buscar número de referencia
    operacion = re.search(r"(?:Número de operación|Número de referencia)[\s:]*([\d]{6,})", texto, re.IGNORECASE)
    datos["operacion"] = operacion.group(1).strip() if operacion else None

    # 💳 Buscar titular emisor
    titular = re.search(r"Titular\s*\n*([^\n]+)", texto, re.IGNORECASE)
    if titular:
        datos["emisor_nombre"] = titular.group(1).strip()

    # 🏦 Buscar cuenta de origen
    cuenta_origen = re.search(r"Cuenta de origen\s*\n*([^\n]+)", texto, re.IGNORECASE)
    if cuenta_origen:
        datos["emisor_cuenta_origen"] = cuenta_origen.group(1).strip()

    # Log final
    print("📦 Datos extraídos [GENÉRICO]:")
    for k, v in datos.items():
        print(f"   - {k}: {v}")

    return datos
