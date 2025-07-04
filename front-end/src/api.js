import { getToken } from "./auth.js";

const API_BASE = import.meta.env.VITE_API_BASE ?? '';


// Utilidad para hacer fetch con headers automáticos
async function apiFetch(endpoint, options = {}) {
  const headers = options.headers || {};

  // Agregar token si hay
  const token = getToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  // Agregar Content-Type si no es FormData
  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (res.status === 401) {
    localStorage.removeItem("token");
    const toastEl = document.getElementById("toastSesionExpirada");
    if (toastEl) {
      const toast = new bootstrap.Toast(toastEl);
      toast.show();
    }
    setTimeout(() => {
      window.location.href = "/login.html";
    }, 3000);
    throw new Error("Sesión expirada");
  }

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.error || "Error en la solicitud");
  }

  return res.json();
}

// 🔹 Obtener lista de profesores
export async function getProfesores() {
  const data = await apiFetch("/profesores");
  return data.profesores || [];
}

// 🔹 Obtener turnos disponibles por profesor
export async function getDisponibilidad(profesorId, inicio, fin) {
  const params = new URLSearchParams({ profesor_id: profesorId });
  if (inicio) params.append("inicio", inicio);
  if (fin) params.append("fin", fin);

  const data = await apiFetch(`/turnos/disponibles?${params.toString()}`);
  return data.turnos || [];
}


// 🔹 Reservar un turno temporal (con turnoId o con profesor + fecha + hora)
export async function reservarTurnoTemporal(payload) {
  return apiFetch("/turnos/reservar-temporal", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

// 🔹 Confirmar reserva con turno ya existente
export async function reservarTurno(turnoId) {
  return apiFetch("/turnos/reservar", {
    method: "POST",
    body: JSON.stringify({ turno_id: turnoId }),
  });
}


// 🔹 Subir comprobante de transferencia
export async function subirComprobante(turnoId, archivo) {
  const formData = new FormData();
  formData.append("turno_id", turnoId);
  formData.append("comprobante", archivo);
  console.log("📤 Enviando FormData:");
  for (let [key, value] of formData.entries()) {
    console.log(`   ${key}:`, value);
  }
  return apiFetch("/turnos/subir-comprobante", {
    method: "POST",
    body: formData,
  });
}

