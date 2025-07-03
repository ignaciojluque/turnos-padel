# Backend — Turnos Pádel 🎾

Este backend gestiona autenticación, reserva de turnos y validación automática de comprobantes de pago para clases de pádel. Está construido con Flask, SQLAlchemy y procesamiento OCR estructurado para documentos bancarios.

---

## 🔄 Flujo general

1. `POST /turnos/reservar-temporal` → bloquea un turno como pendiente por 15 minutos.
2. `POST /turnos/subir-comprobante` → recibe un archivo, detecta banco, valida datos y marca estado_pago = subido.
3. `POST /turnos/reservar` → si el turno está pendiente + pago subido, lo confirma.
4. `POST /turnos/<id>/liberar` → lo restablece como libre (admin).

---

## 📁 Estructura del proyecto

back-end/
├── app/
│   ├── __init__.py               # create_app(), configuración de CORS, registros
│   ├── models.py                 # Modelos SQLAlchemy: Usuario, Turno, Profesor, Comprobante
│   ├── routes/
│   │   ├── auth_routes.py        # Autenticación: login, registro, refresh, logout
│   │   ├── turnos_routes.py      # Reservas, carga de comprobantes, liberación de turnos
│   │   └── profesores_routes.py  # Listado de profesores
│   ├── parsers/
│   │   ├── bbva.py
│   │   ├── galicia.py
│   │   ├── mercado_pago.py
│   │   ├── generico.py
│   │   └── __init__.py
│   └── utils/
│       ├── comprobantes_utils.py   # Extracción y validación de texto bancario
│       ├── fecha_utils.py          # Utilidades de datetime
│       ├── hashing.py              # SHA-256 para evitar duplicados
│       ├── jwt_utils.py            # JWT y protección de rutas
│       └── validacion_comun.py     # Validaciones compartidas
├── comprobantes/                  # PDF o imágenes de comprobantes subidos
├── migrations/                    # Migraciones de base de datos
├── config.py                      # Configuración por entorno
├── requirements.txt               # Dependencias Python
├── .env                           # Variables de entorno locales
└── README.md                      # Este archivo

---

## 🧬 Modelos

- **Usuario** → nombre, email, contraseña, relación con turnos
- **Profesor** → nombre, relación con turnos
- **Turno** → estado (`libre`, `pendiente`, `confirmado`), fecha, hora, usuario, comprobante
- **Comprobante** → hash, datos bancarios, estado validado
- **RefreshToken** → seguridad de sesión

---

## 🔐 Autenticación (`/auth`)

| Método | Ruta           | Descripción                    |
|--------|----------------|--------------------------------|
| POST   | /login         | Login con JWT                  |
| POST   | /registro      | Registro de nuevo usuario      |
| POST   | /refresh       | Renueva access token (desde cookie) |
| POST   | /logout        | Revoca refresh token           |

---

## 🎾 Turnos (`/turnos`)

| Método | Ruta                         | Descripción                                 |
|--------|------------------------------|---------------------------------------------|
| GET    | /disponibles?profesor_id=X  | Ver turnos libres de un profesor            |
| GET    | /mios                       | Ver turnos del usuario logueado             |
| POST   | /reservar-temporal         | Reserva el turno por 15 minutos             |
| POST   | /subir-comprobante         | Subida del archivo y validación automática  |
| POST   | /reservar                  | Confirmación final del turno                |
| POST   | /<id>/liberar              | Libera turno (admin), borra asignación y archivo |

---

## 📥 Validación de comprobantes

- Se aceptan `.pdf`, `.jpg`, `.png`
- Se detecta el proveedor (ej: MercadoPago, BBVA, Galicia)
- Se extraen:
  - monto transferido
  - CBU/CVU
  - nombre destinatario
  - fecha
  - número de operación
- Se valida contra datos esperados
- Se genera un hash SHA-256 para evitar duplicados

---

## 📊 Estados del turno

| estado       | estado_pago | Significado                               |
|--------------|-------------|-------------------------------------------|
| libre        | pendiente   | Disponible para ser reservado             |
| pendiente    | pendiente   | Reservado por usuario, sin comprobante    |
| pendiente    | subido      | Comprobante validado, esperando confirmación |
| confirmado   | completo    | Turno totalmente validado y confirmado    |

---

## ⚙️ Configuración (`.env`)

FLASK_ENV=development 
SECRET_KEY=clave_secreta 
SQLALCHEMY_DATABASE_URI=sqlite:///base.db 
MERCADO_PAGO_TOKEN=xxx 
TURNO_EXPIRA_MINUTOS=15 API_ORIGINS=http://localhost:5173


---

## 🌐 CORS

Configurado con:

```python
CORS(app, origins=[...], supports_credentials=True)

@app.after_request
def agregar_headers_cors(response):
    origin = request.headers.get("Origin")
    if origin == "http://localhost:5173":
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response
