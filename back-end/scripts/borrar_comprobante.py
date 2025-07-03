import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import create_app, db
from app.models import Comprobante
app = create_app()
app.app_context().push()

def borrar_comprobante_por_hash(hash_val):
    comprobante = Comprobante.query.filter_by(hash_archivo=hash_val).first()

    if not comprobante:
        print("❌ No se encontró ningún comprobante con ese hash.")
        return

    print(f"🧻 Borrando comprobante con hash: {hash_val}")

    # 🔄 Limpiar turno asociado si existe
    turno = comprobante.turno
    if turno:
        print(f"↩️ Limpieza del turno asociado (ID: {turno.id})")
        turno.comprobante_url = None
        turno.estado_pago = "pendiente"

    # 🧨 Eliminar archivo físico si existe
    ruta_archivo = turno.comprobante_url if turno else None
    if ruta_archivo and os.path.exists(ruta_archivo):
        try:
            os.remove(ruta_archivo)
            print(f"🗑️ Archivo físico eliminado: {ruta_archivo}")
        except Exception as e:
            print(f"⚠️ No se pudo eliminar el archivo: {e}")

    db.session.delete(comprobante)
    db.session.commit()
    print("✅ Comprobante eliminado correctamente.")

if __name__ == "__main__":
    # Reemplazá este hash por el que querés borrar
    hash_a_borrar = "d5c98df8789358b2f0cd6ec4127da174474fe08d8bc975b4e4d79d8d0fddbb04"
    borrar_comprobante_por_hash(hash_a_borrar)
