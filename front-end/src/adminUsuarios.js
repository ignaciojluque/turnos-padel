const API_BASE = import.meta.env.VITE_API_BASE ?? '';

function getToken() {
  return localStorage.getItem("token");
}

async function apiFetch(endpoint, options = {}) {
  const headers = options.headers || {};
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;
  if (!(options.body instanceof FormData)) headers["Content-Type"] = "application/json";

  const res = await fetch(`${API_BASE}${endpoint}`, { ...options, headers });

  if (res.status === 401) {
    localStorage.clear();
    alert("⚠️ Sesión expirada. Serás redirigido al login.");
    window.location.href = "/login.html";
    throw new Error("Sesión expirada");
  }

  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.error || "Error en la solicitud");
  }

  return res.json();
}

// 🧑‍💼 Cargar usuarios al iniciar
window.addEventListener("DOMContentLoaded", async () => {
  try {
    const data = await apiFetch("/usuarios");
    renderUsuarios(data.usuarios);

    const inputFiltro = document.getElementById("filtroUsuario");
    inputFiltro.addEventListener("input", () => {
      const termino = inputFiltro.value.toLowerCase();
      const filtrados = data.usuarios.filter((u) =>
        u.nombre.toLowerCase().includes(termino) ||
        u.email.toLowerCase().includes(termino)
      );
      renderUsuarios(filtrados);
    });
  } catch (err) {
    alert("❌ No se pudieron cargar los usuarios: " + err.message);
  }
});

// 🧾 Renderizar tabla de usuarios
function renderUsuarios(usuarios) {
  const tbody = document.getElementById("tablaUsuarios");
  tbody.innerHTML = "";

  usuarios.forEach((u) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${u.nombre}</td>
      <td>${u.email}</td>
      <td>${u.telefono}</td>
      <td>${u.es_admin ? "✅" : "❌"}</td>
      <td>${u.modo_test ? "🧪 Sí" : "–"}</td>
      <td>
        <button class="btn btn-outline-info btn-sm" onclick="toggleModoTest(${u.id}, ${!u.modo_test})">
          ${u.modo_test ? "Desactivar" : "Activar"}
        </button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

// 🔘 Cambiar modo test de un usuario
window.toggleModoTest = async (usuarioId, activar) => {
  const confirmar = confirm(`¿${activar ? "Activar" : "Desactivar"} modo test para este usuario?`);
  if (!confirmar) return;

  try {
    await apiFetch(`/usuarios/${usuarioId}/modo-test`, {
      method: "POST",
      body: JSON.stringify({ activar })
    });
    location.reload();
  } catch (err) {
    alert("❌ Error al cambiar modo test: " + err.message);
  }
};
