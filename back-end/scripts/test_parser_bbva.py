import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import fitz  # PyMuPDF
from parsers import bbva  # Asegurate que bbva.py tenga extraer_datos()

def leer_pdf_a_texto(ruta_pdf):
    doc = fitz.open(ruta_pdf)
    texto = ""
    for pagina in doc:
        texto += pagina.get_text()
    return texto

def testear_bbva():
    texto = leer_pdf_a_texto("comprobanteBBVA.pdf")
    print("🧾 Texto extraído del PDF:")
    print(texto[:500])  # Mostramos las primeras líneas por si querés ver cómo viene

    datos = bbva.extraer_datos(texto)
    print("\n🔍 Datos extraídos por el parser:")
    for k, v in datos.items():
        print(f"{k}: {v}")

if __name__ == "__main__":
    testear_bbva()
