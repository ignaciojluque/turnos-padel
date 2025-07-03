const API_BASE = import.meta.env.VITE_API_BASE;

/**
 * Inicia sesión con email y contraseña
 * Guarda el token y es_admin en localStorage si es exitoso
 */
export async function login(email, password) {
  try {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password: password }),
    });

    if (!res.ok) {
      let data = {};
      try {
        data = await res.json();
      } catch {}
      throw new Error(data.error || "Error al iniciar sesión");
    }

    const data = await res.json();
    localStorage.setItem("token", data.access_token);

    // 🔐 Guardar es_admin como "true" o "false"
    const esAdmin = data.usuario?.es_admin === true || data.usuario?.es_admin === 1;
    localStorage.setItem("es_admin", String(esAdmin));

    return true;
  } catch (err) {
    console.error("Error en login:", err.message);
    throw err;
  }
}

/**
 * Devuelve el token almacenado localmente
 */
export function getToken() {
  return localStorage.getItem("token");
}

/**
 * Verifica si hay token, si no, redirige al login
 */
export function verificarLogin() {
  const token = getToken();
  if (!token) {
    window.location.href = "/login.html";
  }
}

/**
 * Limpia el token y redirige al login
 */
export function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("es_admin"); // 🧼 limpieza extra
  window.location.href = "/login.html";
}
