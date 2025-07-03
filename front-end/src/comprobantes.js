import { subirComprobante, reservarTurno, getDisponibilidad } from "./api.js";
import { mostrarMensaje, simularBarraCarga } from "./ui.js";
import { actualizarEventos, marcarTurnoComoOcupado } from "./calendar.js";

let turnoEnCurso = {
  id: null,
  profesorId: null,
  fecha: null,
  hora: null,
};

export function setTurnoTemporal({ turnoId, profesorId, fecha, hora }) {
  turnoEnCurso = { id: turnoId, profesorId, fecha, hora };
}

export function getTurnoTemporal() {
  return turnoEnCurso;
}

export function inicializarComprobante() {
  const btn = document.getElementById("btnSubirComprobante");
  const input = document.getElementById("comprobanteInput");
  const estado = document.getElementById("estadoComprobante");
  const barraDiv = document.querySelector(".progress");
  const barraInterna = document.getElementById("barraCarga");
  const alerta = document.getElementById("alertaTurno");

  if (!btn || !input || !estado) return;

  btn.addEventListener("click", async () => {
    const archivo = input.files[0];
    if (!archivo || !turnoEnCurso?.id) {
      mostrarMensaje(estado, "⚠️ Faltan datos: seleccioná comprobante y turno.", "danger");
      return;
    }

    try {
      mostrarMensaje(estado, "⏳ Comprobante en revisión…", "info");
      simularBarraCarga(barraDiv, barraInterna);

      const respuesta = await subirComprobante(turnoEnCurso.id, archivo);

      if (respuesta?.mensaje?.includes("✅")) {
        mostrarMensaje(estado, "✅ Comprobante verificado correctamente.", "success");

        try {
          await reservarTurno(turnoEnCurso.id);

          alerta.textContent = "✅ Tu turno ya se encuentra reservado.";
          alerta.classList.remove("alert-danger");
          alerta.classList.add("alert-success");
          alerta.style.display = "block";

          marcarTurnoComoOcupado(turnoEnCurso.fecha, turnoEnCurso.hora);

          setTimeout(() => {
            alerta.style.display = "none";
          }, 3000);

          const modal = bootstrap.Modal.getInstance(document.getElementById("modalPago"));
          if (modal) modal.hide();

        } catch (reservaError) {
          console.error("❌ Error al reservar turno:", reservaError);
          alerta.textContent = "❌ El comprobante fue aceptado, pero no se pudo reservar el turno.";
          alerta.classList.remove("alert-success");
          alerta.classList.add("alert-danger");
          alerta.style.display = "block";
        }

      } else {
        const motivos = respuesta?.motivos || [];
        const detalle = motivos.map(m => `• ${m}`).join("<br>");
        mostrarMensaje(estado, `❌ El comprobante no fue válido.<br>${detalle}`, "danger");

        alerta.textContent = "❌ El comprobante fue rechazado.";
        alerta.classList.remove("alert-success");
        alerta.classList.add("alert-danger");
        alerta.style.display = "block";
        setTimeout(() => {
          alerta.style.display = "none";
        }, 4000); // podés ajustar el tiempo si querés
      }

      const turnos = await getDisponibilidad(turnoEnCurso.profesorId);
      actualizarEventos(turnos);

    } catch (err) {
      console.error("🧨 Error en la subida:", err);
      mostrarMensaje(estado, "❌ Error al subir el comprobante: " + (err.message || "desconocido"), "danger");
    } finally {
      setTimeout(() => {
        barraDiv.style.display = "none";
        barraInterna.style.width = "0%";
      }, 1500);
    }
  });
}

export function clearTurnoTemporal() {
  localStorage.removeItem("turnoTemporal");
}
