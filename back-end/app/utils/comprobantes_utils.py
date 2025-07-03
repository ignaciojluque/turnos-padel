from PyPDF2 import PdfReader
from PIL import Image
import pytesseract, os
from datetime import datetime, timedelta
from app.utils.validacion_comun import validar_campos_comunes
from app.utils.hashing import hash_archivo
from app.parsers import detectar_proveedor, get_parser_por_proveedor

def leer_texto_pdf(ruta):
    reader = PdfReader(ruta)
    return "".join(page.extract_text() for page in reader.pages if page.extract_text())

def leer_texto_imagen(ruta):
    imagen = Image.open(ruta)
    return pytesseract.image_to_string(imagen)

def procesar_comprobante(ruta_archivo, config, modo_flexible=False):

    ext = os.path.splitext(ruta_archivo)[1].lower()
    texto = leer_texto_pdf(ruta_archivo) if ext == ".pdf" else leer_texto_imagen(ruta_archivo)

    proveedor = detectar_proveedor(texto)
    print(f"🔍 Proveedor detectado: {proveedor}") 

    parser = get_parser_por_proveedor(proveedor)
    print(f"🧠 Usando parser: {parser.__name__}")
    datos = parser(texto)

    es_valido, motivos = validar_campos_comunes(datos, config, modo_flexible)
    
    huella = hash_archivo(ruta_archivo)

    return es_valido, datos, huella, motivos
