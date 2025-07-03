import sys
import os
from datetime import datetime

# Agregamos la carpeta raíz al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app, db
from models import Turno

app = create_app()
app.app_context().push()

def liberar_turnos_expirados():
    ahora = datetime.utcnow()
    vencidos = Turno.query.filter(
        Turno.estado == "pendiente",
        Turno.fecha_expiracion < ahora,
        Turno.estado_pago == "pendiente"
    ).all()

    if not vencidos:
        print("✅ No hay turnos vencidos para liberar.")
        return

    print(f"🧹 Liberando {len(vencidos)} turno(s) expirado(s)...")
    for t in vencidos:
        print(f" - Turno ID {t.id} liberado.")
        t.estado = "libre"
        t.fecha_expiracion = None

    db.session.commit()
    print("🎉 Turnos liberados exitosamente.")

if __name__ == "__main__":
    liberar_turnos_expirados()
