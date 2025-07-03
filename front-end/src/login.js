import { login } from "./auth.js";
import {
  mostrarMensaje,
  mostrarSpinner,
  ocultarSpinner,
} from "./ui.js";

document.addEventListener("DOMContentLoaded", () => {
  ocultarSpinner("spinnerLogin");

  const emailInput = document.getElementById("emailInput");
  const passwordInput = document.getElementById("passwordInput");
  const btnLogin = document.getElementById("btnLogin");
  const loginError = document.getElementById("loginError");

  btnLogin.addEventListener("click", async () => {
    const email = emailInput.value.trim();
    const password = passwordInput.value.trim();

    if (!email || !password) {
      mostrarMensaje(loginError, "Completá los campos", "danger");
      return;
    }

    const spinner = document.getElementById("spinnerLogin");
    spinner.classList.remove("d-none");
    btnLogin.disabled = true;
    loginError.textContent = "";

    try {
      await login(email, password);
      window.location.href = "/index.html";
    } catch (err) {
      mostrarMensaje(loginError, err.message || "Error al iniciar sesión", "danger");
    } finally {
      spinner.classList.add("d-none");
      btnLogin.disabled = false;
    }
  });
});
