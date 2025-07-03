import { getProfesores, getDisponibilidad, subirComprobante } from "./api.js";
import { inicializarCalendario, actualizarEventos, refrescarSemanaVisible } from "./calendar.js";
import { verificarLogin } from "./auth.js";
import { poblarSelectProfesores, ocultarSpinner } from "./ui.js";
import { inicializarComprobante, getTurnoTemporal } from "./comprobantes.js";
import * as bootstrap from "bootstrap";

window.bootstrap = bootstrap;
verificarLogin();

document.addEventListener("DOMContentLoaded", async () => {
  const selectProfe = document.getElementById("profesorSelect");
  const profesores = await getProfesores();
  ocultarSpinner();
  poblarSelectProfesores(selectProfe, profesores);
  inicializarCalendario();
  inicializarComprobante();

  selectProfe.addEventListener("change", async (e) => {
    const profesorId = e.target.value;
    const turnos = await getDisponibilidad(profesorId);
    actualizarEventos(turnos);
  });

  if (localStorage.getItem("turnoLiberado") === "true") {
    const profesorId = document.getElementById("profesorSelect").value;
    if (profesorId) {
      const turnos = await getDisponibilidad(profesorId);
      actualizarEventos(turnos);
      localStorage.removeItem("turnoLiberado");
    }
  }

  // 🎯 Manejo del botón "Subir comprobante"
  let comprobanteEnProceso = false;

  const modal = document.getElementById("modalPago");

  modal.addEventListener("hidden.bs.modal", async () => {
    console.log("📪 Modal cerrado");
    if (!comprobanteEnProceso) {
      console.log("🧼 Limpiando inputs del modal...");
      document.getElementById("estadoComprobante").innerText = "";
      document.getElementById("comprobanteInput").value = "";
      document.getElementById("preview").innerHTML = "";
    }

    try {
      await refrescarSemanaVisible();
    } catch (err) {
      console.error("❌ Error al refrescar calendario tras cierre de modal:", err);
    }
  });

  window.addEventListener("focus", async () => {
    const turno = getTurnoTemporal();
  
    if (!turno?.turnoId) {
      console.log("🟢 No hay turno temporal activo, nada que liberar.");
      return;
    }
  
    try {
      const res = await fetch(`${import.meta.env.VITE_API_BASE}/turnos/${turno.turnoId}/liberar-si-pendiente`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
          "Content-Type": "application/json"
        }
      });
      const data = await res.json();
  
      if (res.status === 403 && data?.error?.includes("No tenés permiso")) {
        console.log("⏹️ Turno ya fue liberado (o no pertenece al usuario). Silenciando.");
        return;
      }
  
      console.log("♻️ Resultado de liberar turno:", data);
    } catch (err) {
      console.warn("❌ Error al liberar turno:", err);
    }
  
    const modal = document.getElementById("modalPago");
    const instanciaModal = bootstrap.Modal.getInstance(modal);
    if (instanciaModal) instanciaModal.hide();
  });  
});
