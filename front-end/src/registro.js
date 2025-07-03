document.getElementById("formRegistro").addEventListener("submit", async (e) => {
  e.preventDefault();

  const nombre = document.getElementById("nombre").value;
  const telefono = document.getElementById("telefono").value;
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  const errorDiv = document.getElementById("errorRegistro");

  try {
    console.log("📤 Enviando datos:", { nombre, telefono, email, password });

    const res = await fetch(import.meta.env.VITE_API_BASE + "/auth/registro", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nombre, telefono, email, password }),
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Error al registrar");

    alert("✅ Registro exitoso. Ya podés iniciar sesión.");
    window.location.href = "/login.html";
  } catch (err) {
    errorDiv.textContent = err.message;
  }
});
