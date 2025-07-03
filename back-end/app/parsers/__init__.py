from .mercado_pago import extraer_datos as mercado_pago_parser
from .galicia import extraer_datos as galicia_parser
from .bbva import extraer_datos as bbva_parser
from .santander import extraer_datos as santander_parser
from .hsbc import extraer_datos as hsbc_parser
from .brubank import extraer_datos as brubank_parser
from .uala import extraer_datos as uala_parser
from .modo import extraer_datos as modo_parser
from .generico import extraer_datos as generico_parser

def detectar_proveedor(texto):
    t = texto.lower()
    if "mercado pago" in t:
        return "mercado_pago"
    if "galicia" in t:
        return "galicia"
    if "bbva" in t:
        return "bbva"
    if "santander" in t:
        return "santander"
    if "hsbc" in t:
        return "hsbc"
    if "brubank" in t:
        return "brubank"
    if "uala" in t:
        return "uala"
    if "modo" in t:
        return "modo"
    return "generico"

def get_parser_por_proveedor(nombre):
    return {
        "mercado_pago": mercado_pago_parser,
        "galicia": galicia_parser,
        "bbva": bbva_parser,
        "santander": santander_parser,
        "hsbc": hsbc_parser,
        "brubank": brubank_parser,
        "uala": uala_parser,
        "modo": modo_parser,
        "generico": generico_parser
    }.get(nombre, generico_parser)
