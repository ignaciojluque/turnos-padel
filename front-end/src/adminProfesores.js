const API_BASE = import.meta.env.VITE_API_BASE;

// 🔐 Obtener token desde localStorage
function getToken() {
  return localStorage.getItem("token");
}

// 🌐 Utilidad central de fetch con manejo de sesión
async function apiFetch(endpoint, options = {}) {
  const headers = options.headers || {};
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;
  if (!(options.body instanceof FormData)) headers["Content-Type"] = "application/json";

  const res = await fetch(`${API_BASE}${endpoint}`, { ...options, headers });

  if (res.status === 401) {
    localStorage.removeItem("token");
    alert("⚠️ Sesión expirada. Redirigiendo...");
    setTimeout(() => {
      window.location.href = "/login.html";
    }, 1500);
    throw new Error("Sesión expirada");
  }

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.error || "Error en la solicitud");
  }

  return res.json();
}

// Estado local
const rangos = [];
const bloqueos = [];

// Añadir nuevo rango horario
window.agregarRango = () => {
  const container = document.createElement("div");
  container.className = "rango";
  container.innerHTML = `
    Día:
    <select class="dia">
      <option value="0">Lunes</option>
      <option value="1">Martes</option>
      <option value="2">Miércoles</option>
      <option value="3">Jueves</option>
      <option value="4">Viernes</option>
      <option value="5">Sábado</option>
      <option value="6">Domingo</option>
    </select>
    Desde: <input type="time" class="hora-inicio" />
    Hasta: <input type="time" class="hora-fin" />
  `;
  document.getElementById("rangosContainer").appendChild(container);
};

// Añadir bloqueo
window.agregarBloqueo = () => {
  const fecha = document.getElementById("fechaBloqueo").value;
  const motivo = document.getElementById("motivoBloqueo").value;
  if (!fecha) return alert("Elegí una fecha válida");

  bloqueos.push({ fecha, motivo });

  const li = document.createElement("li");
  li.textContent = `${fecha} (${motivo})`;
  document.getElementById("bloqueosList").appendChild(li);

  document.getElementById("fechaBloqueo").value = "";
  document.getElementById("motivoBloqueo").value = "";
};

// Validación de solapamiento
function verificarSolapamientos(rangos) {
  const porDia = {};
  for (const r of rangos) {
    const k = r.dia_semana;
    if (!porDia[k]) porDia[k] = [];
    porDia[k].push(r);
  }

  for (const dia in porDia) {
    const horarios = porDia[dia]
      .map(r => [r.hora_inicio, r.hora_fin])
      .sort((a, b) => a[0].localeCompare(b[0]));
    for (let i = 1; i < horarios.length; i++) {
      if (horarios[i][0] < horarios[i - 1][1]) return true;
    }
  }
  return false;
}

// Enviar profesor al backend
window.enviarProfesor = async () => {
  const nombre = document.getElementById("nombreProfesor").value;
  const especialidad = document.getElementById("especialidadProfesor").value;
  const contenedores = document.querySelectorAll(".rango");
  const rangosFinal = [];

  contenedores.forEach(div => {
    const dia = parseInt(div.querySelector(".dia").value);
    const hora_inicio = div.querySelector(".hora-inicio").value;
    const hora_fin = div.querySelector(".hora-fin").value;
    if (hora_inicio && hora_fin) {
      rangosFinal.push({ dia_semana: dia, hora_inicio, hora_fin });
    }
  });

  if (verificarSolapamientos(rangosFinal)) {
    document.getElementById("errorRangos").textContent = "⚠️ Rangos solapados detectados. Corregilos antes de guardar.";
    return;
  } else {
    document.getElementById("errorRangos").textContent = "";
  }

  const payload = {
    nombre,
    especialidad,
    disponibilidades: rangosFinal,
    bloqueos
  };

  try {
    const res = await apiFetch("/administrar-profesores", {
      method: "POST",
      body: JSON.stringify(payload)
    });
    alert(res.mensaje || "✅ Profesor creado correctamente");
    window.location.reload();
  } catch (err) {
    alert("❌ Error al crear profesor: " + err.message);
  }
};

// 🔄 Cargar profesores existentes
async function cargarProfesores() {
  const contenedor = document.getElementById("profesoresExistentes");
  contenedor.innerHTML = "<p>Cargando...</p>";

  try {
    const data = await apiFetch("/profesores");
    const profesores = data.profesores;
    if (profesores.length === 0) {
      contenedor.innerHTML = "<p>No hay profesores registrados aún.</p>";
      return;
    }

    contenedor.innerHTML = "";
    profesores.forEach(p => {
      const div = document.createElement("div");
      div.className = "profesor";
      div.innerHTML = `
        <strong>${p.nombre}</strong> – ${p.especialidad || "Sin especialidad"}
        <button class="btn-eliminar" data-id="${p.id}">🗑️ Borrar</button>
      `;
      contenedor.appendChild(div);
    });

    // Agregar handlers de borrado
    document.querySelectorAll(".btn-eliminar").forEach(btn => {
      btn.addEventListener("click", async () => {
        const id = btn.dataset.id;
        const confirmar = confirm("¿Seguro que querés eliminar este profesor?");
        if (!confirmar) return;

        try {
          const res = await apiFetch(`/administrar-profesores/${id}`, {
            method: "DELETE"
          });
          alert(res.mensaje || "Profesor eliminado");
          cargarProfesores(); // refrescar la lista
        } catch (err) {
          alert("❌ Error al eliminar: " + err.message);
        }
      });
    });

  } catch (err) {
    contenedor.innerHTML = `<p>❌ Error: ${err.message}</p>`;
  }
}

window.addEventListener("DOMContentLoaded", cargarProfesores);
