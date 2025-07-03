const API_BASE = import.meta.env.VITE_API_BASE;

// 🔐 Obtener token desde localStorage
function getToken() {
  return localStorage.getItem("token");
}

// 🌐 Fetch con headers y manejo de sesión
async function apiFetch(endpoint, options = {}) {
  const headers = options.headers || {};
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;
  if (!(options.body instanceof FormData)) headers["Content-Type"] = "application/json";

  const res = await fetch(`${API_BASE}${endpoint}`, { ...options, headers });

  if (res.status === 401) {
    localStorage.removeItem("token");
    alert("⚠️ Sesión expirada. Serás redirigido al login.");
    setTimeout(() => {
      window.location.href = "/login.html";
    }, 1500);
    throw new Error("Sesión expirada");
  }

  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.error || "Error en la solicitud");
  }

  return res.json();
}

// ⚙️ Cargar configuración al iniciar
window.addEventListener("DOMContentLoaded", async () => {
  try {
    const config = await apiFetch("/auth/configuracion-pago");
    document.getElementById("nombreDest").value = config.destinatario || "";
    document.getElementById("cbu").value = config.cbu || "";
    document.getElementById("monto").value = config.monto_esperado || "";
    document.getElementById("tiempo").value = config.tiempo_maximo_minutos || "";

    await cargarPagos();
    await cargarTurnosPendientes();
  } catch (err) {
    alert("❌ No se pudo cargar configuración: " + err.message);
  }
});

// 💾 Guardar nueva configuración
window.guardarConfiguracion = async () => {
  const payload = {
    destinatario: document.getElementById("nombreDest").value,
    cbu: document.getElementById("cbu").value,
    monto_esperado: parseFloat(document.getElementById("monto").value),
    tiempo_maximo_minutos: parseInt(document.getElementById("tiempo").value),
  };

  try {
    await apiFetch("/auth/configuracion-pago", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    alert("✅ Configuración guardada");
  } catch (err) {
    alert("❌ Error al guardar configuración: " + err.message);
  }
};

// 📄 Cargar historial de pagos
async function cargarPagos() {
  try {
    const pagos = await apiFetch("/auth/pagos");
    const tabla = document.getElementById("tablaPagos");
    tabla.innerHTML = "";

    pagos.forEach((pago) => {
      const tr = document.createElement("tr");

      const botonValidar = document.createElement("button");
      botonValidar.textContent = "Validar";
      botonValidar.className = "btn btn-sm btn-outline-success";
      botonValidar.addEventListener("click", () => validarPago(pago.id));

      tr.innerHTML = `
        <td>${pago.usuario_email || "-"}</td>
        <td>${new Date(pago.fecha).toLocaleString()}</td>
        <td>$${pago.monto?.toFixed(2) || "-"}</td>
        <td>${pago.estado}</td>
        <td>${pago.cbu || "-"}</td>
        <td></td>
      `;

      if (pago.estado === "pendiente") {
        tr.children[5].appendChild(botonValidar);
      } else {
        tr.children[5].textContent = "✔️";
      }

      tabla.appendChild(tr);
    });
  } catch (err) {
    alert("❌ Error al cargar pagos: " + err.message);
  }
}


// ✅ Validar pago del modelo Pago
window.validarPago = async (pagoId) => {
  const confirmar = confirm("¿Marcar este pago como validado manualmente?");
  if (!confirmar) return;

  try {
    await apiFetch(`auth/pagos/${pagoId}/validar`, { method: "POST" });
    alert("✅ Pago validado");
    cargarPagos();
  } catch (err) {
    alert("❌ Error al validar: " + err.message);
  }
};

// 🔁 Cargar turnos con comprobante subido
async function cargarTurnosPendientes() {
  try {
    const data = await apiFetch("/pagos/pendientes");
    const tabla = document.getElementById("tablaTurnosPendientes");
    const mensajeVacio = document.getElementById("mensajeVacioTurnos");

    tabla.innerHTML = "";
    mensajeVacio.style.display = "none";

    if (!data.pendientes.length) {
      mensajeVacio.style.display = "block";
      return;
    }

    data.pendientes.forEach((turno) => {
      const tr = document.createElement("tr");

      const botonVer = document.createElement("button");
      botonVer.className = "btn btn-link text-info p-0";
      botonVer.textContent = "📎 Ver";
      botonVer.addEventListener("click", () => verComprobante(turno.id));

      const botonConfirmar = document.createElement("button");
      botonConfirmar.className = "btn btn-success btn-sm";
      botonConfirmar.textContent = "✅ Completar";
      botonConfirmar.addEventListener("click", () => confirmarTurno(turno.id));

      tr.innerHTML = `
        <td>${turno.usuario_nombre || "-"}</td>
        <td>${turno.usuario_email || "-"}</td>
        <td>${turno.comprobante?.emisor_nombre || "(sin emisor)"}</td>
        <td>${turno.comprobante?.emisor_cbu || "(sin CBU)"}</td>
        <td></td>
        <td></td>
      `;

      tr.children[4].appendChild(botonVer);
      tr.children[5].appendChild(botonConfirmar);

      tabla.appendChild(tr);
    });
  } catch (err) {
    console.error("❌ Error cargando turnos pendientes:", err);
  }
}


// ✅ Confirmar manualmente que un turno está pagado
window.confirmarTurno = async (turnoId) => {
  const confirmar = confirm("¿Confirmás que este turno ya fue pagado y es válido?");
  if (!confirmar) return;

  try {
    await apiFetch(`/${turnoId}/confirmar-pago`, {
      method: "POST"
    });
    alert("✅ Turno marcado como pago completo");
    cargarTurnosPendientes();
  } catch (err) {
    alert("❌ Error al completar pago del turno: " + err.message);
  }
};

// 📎 Ver comprobante en nueva ventana
async function verComprobante(turnoId) {
  const token = getToken();
  try {
    const res = await fetch(`${API_BASE}/turnos/comprobantes/${turnoId}`, {
      headers: { Authorization: "Bearer " + token }
    });

    if (!res.ok) {
      alert("❌ No se pudo mostrar el comprobante");
      return;
    }

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    window.open(url, "_blank", "noopener");
  } catch (err) {
    alert("❌ Error al mostrar comprobante: " + err.message);
  }
}
