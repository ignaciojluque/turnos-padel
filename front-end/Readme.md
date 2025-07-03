# 🖥️ Frontend — Turnos Pádel 🎾

Este frontend ofrece una interfaz simple y fluida para la reserva de clases de pádel, incluyendo selección de profesor, visualización de calendario, subida de comprobantes bancarios y validación automática. Está construido en JavaScript nativo con módulos ES, usando **Vite** para desarrollo, y **Bootstrap** para el diseño.

---

## 🗂️ Estructura general
front-end
├── index.html            # Página principal (calendario y reservas)
├── login.html            # Login de usuario
├── registro.html         # Alta de usuario nuevo
├── /src
│   ├── api.js            # Abstracción de llamadas al backend
│   ├── auth.js           # Manejo de login, token y logout
│   ├── calendar.js       # FullCalendar + reserva de turnos
│   ├── comprobantes.js   # Subida y validación del comprobante
│   ├── login.js          # Lógica de login
│   ├── main.js           # Lógica principal de reserva
│   ├── registro.js       # Alta de nuevos usuarios
│   ├── ui.js             # Helpers visuales (mensajes, timers, previews)
│   └── style.css         # Estilos propios del proyecto

---

## 🚦 Flujo de navegación

1. El usuario inicia sesión (`login.html`) o se registra (`registro.html`)
2. Una vez logueado, accede a `index.html`
3. Allí:
   - Selecciona profesor
   - Visualiza turnos disponibles en un calendario semanal (FullCalendar)
   - Al hacer clic en un turno libre, puede reservarlo (temporalmente)
   - Se abre un modal para subir el comprobante de transferencia
   - El sistema verifica el archivo con el backend
   - Si es válido, muestra confirmación y bloquea el turno

---

## 🔌 Comunicación con el backend (`api.js`)

Módulo centralizado para realizar fetchs con token automático:

- `getProfesores()` → GET `/profesores`
- `getDisponibilidad(profesorId)` → GET `/turnos/disponibles`
- `reservarTurnoTemporal(payload)` → POST `/turnos/reservar-temporal`
- `reservarTurno()` → POST `/turnos/reservar`
- `subirComprobante()` → POST `/turnos/subir-comprobante` (FormData)

Gestión automática de errores 401, redirección y toast por sesión expirada.

---

## 🔐 Autenticación (`auth.js`)

- `login(email, password)` → guarda token en `localStorage`
- `verificarLogin()` → redirige si no hay token
- `logout()` → limpia token y redirige
- `getToken()` → obtiene el JWT actual

---

## 📆 Calendario (`calendar.js`)

- Usa FullCalendar en modo `timeGridWeek`
- Eventos "Disponible" (verde) y "No disponible" (rojo)
- Al clickear en uno libre:
  - Se arma payload con turno existente o nuevo
  - Se llama a `reservarTurnoTemporal()`
  - Se inicia temporizador de 15 minutos (vía `ui.js`)
  - Se abre modal para subir comprobante

Funciones clave:
- `inicializarCalendario()` → renderiza calendario
- `actualizarEventos()` → repinta con nuevos turnos
- `marcarTurnoComoOcupado()` → cambia visualmente el turno si se confirma

---

## 🧾 Subida de comprobante (`comprobantes.js`)

- Maneja lógica del botón "Subir comprobante"
- Usa `subirComprobante()` y luego `reservarTurno()` si fue válido
- Muestra mensajes con color, barra de carga y alerta superior
- Cierra el modal automáticamente y actualiza calendario

---

## 🔧 Utilidades visuales (`ui.js`)

- `mostrarMensaje()` → texto coloreado
- `iniciarTemporizador()` → countdown 15:00
- `mostrarVistaPrevia()` → muestra imagen o ícono PDF
- `simularBarraCarga()` → barra de progreso animada
- `poblarSelectProfesores()` → rellena `<select>` de profesores
- `mostrarSpinner()` y `ocultarSpinner()` → para logins y cargas

---

## ✅ Otros

- Archivos `login.js` y `registro.js` manejan sus formularios específicos
- El archivo `counter.js` no es funcional actualmente (demo de Vite)

---

## 📋 Variables de entorno

Usa `import.meta.env.VITE_API_BASE` para determinar la URL del backend. Configurar en `.env`:
VITE_API_BASE=http://localhost:5000


---

## 🎨 Estilos (`style.css`)

Archivo con ajustes personalizados sobre Bootstrap. Define padding, tipografía y detalles visuales como alertas flotantes y previews del comprobante.

---

## 🚀 Comenzar el frontend

Este proyecto usa **Vite**. Para iniciarlo en desarrollo:

```bash
npm install
npm run dev
