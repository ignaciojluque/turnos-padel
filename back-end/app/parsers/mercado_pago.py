import re
from datetime import datetime

def extraer_datos(texto):
    print("🧾 [MercadoPago] Ejecutando extracción personalizada de comprobante...")

    de = re.search(r"·\s*De\s*(.*?)\s*CUIT/CUIL:\s*(\d{2}-\d{8}-\d).*?CVU:\s*(\d{22})", texto, re.DOTALL)
    para = re.search(r"·\s*Para\s*(.*?)\s*CUIT/CUIL:\s*(\d{2}-\d{8}-\d).*?CVU:\s*(\d{22})", texto, re.DOTALL)
    monto = re.search(r"\$\s*([0-9.]+)", texto)
    operacion = re.search(r"Número de operación.*?(\d{6,})", texto, re.IGNORECASE)
    fecha = re.search(r"(\d{1,2} de \w+ de \d{4})\s+a\s+las\s+(\d{1,2}:\d{2})", texto, re.IGNORECASE)

    fecha_hora = None
    if fecha:
        try:
            fecha_hora = datetime.strptime(f"{fecha.group(1)} {fecha.group(2)}", "%d de %B de %Y %H:%M")
        except Exception:
            pass

    return {
        "destinatario_nombre": para.group(1).strip() if para else None,
        "destinatario_cbu": para.group(3).strip() if para else None,
        "monto": monto.group(1).strip() if monto else None,
        "fecha_hora": fecha_hora,
        "operacion": operacion.group(1).strip() if operacion else None,
        "emisor_nombre": de.group(1).strip() if de else None,
        "emisor_cuit": de.group(2).strip() if de else None,
        "emisor_cbu": de.group(3).strip() if de else None
    }
