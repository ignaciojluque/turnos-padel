import { Calendar } from "@fullcalendar/core";
import timeGridPlugin from "@fullcalendar/timegrid";
import esLocale from "@fullcalendar/core/locales/es";
import { iniciarTemporizador } from "./ui.js";
import { reservarTurnoTemporal, getDisponibilidad } from "./api.js";
import { setTurnoTemporal, getTurnoTemporal, clearTurnoTemporal } from "./comprobantes.js";

let calendar = null;

export function inicializarCalendario() {
  const calendarEl = document.getElementById("calendar");

  calendar = new Calendar(calendarEl, {
    plugins: [timeGridPlugin],
    initialView: "timeGridWeek",
    locale: esLocale,
    height: "auto",
    slotMinTime: "7:00:00",
    slotMaxTime: "23:00:00",
    allDaySlot: false,
    headerToolbar: {
      left: "prev,next today",
      center: "title",
      right: ""
    },
    datesSet: async (info) => {
      const profesorId = document.getElementById("profesorSelect").value;
      if (!profesorId) return;
      const start = info.startStr.split("T")[0];
      const end = info.endStr.split("T")[0];
      try {
        const turnos = await getDisponibilidad(profesorId, start, end);
        actualizarEventos(turnos);
      } catch (err) {
        console.warn("❌ Error al actualizar eventos:", err);
      }
    },
    eventClick: (info) => {
      const esAdmin = localStorage.getItem("es_admin") === "true";
      if (info.event.extendedProps.estado === "ocupado" && !esAdmin) return;

      const fechaFormateada = info.event.start.toLocaleDateString();
      const horaFormateada = info.event.start.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

      document.getElementById("turnoSeleccionado").innerHTML = `
        <div class="texto-turno-seleccionado">
          <p><strong>Turno seleccionado:</strong></p>
          <p>${fechaFormateada} a las ${horaFormateada}</p>
          <button class="btn btn-success mt-2" id="btnReservar">Reservar turno</button>
          ${
            esAdmin && info.event.extendedProps.estado === "ocupado"
              ? `<button class="btn btn-danger mt-2 ms-2" id="btnLiberar">Liberar turno</button>`
              : ""
          }
        </div>
      `;

      document.getElementById("btnReservar").addEventListener("click", async () => {
        const profesorId = document.getElementById("profesorSelect").value;
        const fecha = info.event.start.toISOString().split("T")[0];
        const hora = info.event.start.toTimeString().slice(0, 5);
        const turnoId = info.event.id;

        if (!turnoId) {
          alert("Este turno no está disponible aún.");
          return;
        }

        const payload = { turno_id: Number(turnoId) };

        try {
          const respuesta = await reservarTurnoTemporal(payload);

          setTurnoTemporal({
            turnoId: respuesta.turno_id || turnoId,
            profesorId,
            fecha,
            hora,
          });

          iniciarTemporizador(15 * 60, document.getElementById("tiempoRestante"));

          if (esAdmin) {
            try {
              const res = await fetch(`${import.meta.env.VITE_API_BASE}/turnos/${turnoId}/asignar-directo`, {
                method: "POST",
                headers: {
                  Authorization: `Bearer ${localStorage.getItem("token")}`,
                  "Content-Type": "application/json"
                }
              });

              const data = await res.json();
              if (res.ok) {
                alert("✅ Turno reservado como administrador.");
                const turnos = await getDisponibilidad(profesorId);
                actualizarEventos(turnos);
                clearTurnoTemporal();
              } else {
                alert(`❌ ${data.error || "Error al reservar turno como admin"}`);
              }
            } catch (err) {
              console.error("💥", err);
              alert("❌ Error al reservar turno como admin.");
            }
          } else {
            const modal = new bootstrap.Modal(document.getElementById("modalPago"));
            modal.show();
          }
        } catch (err) {
          alert("❌ Error: " + err.message);
        }
      });

      if (esAdmin && info.event.extendedProps.estado === "ocupado") {
        document.getElementById("btnLiberar").addEventListener("click", async () => {
          const confirmar = confirm(`¿Estás seguro de liberar el turno #${info.event.id}?`);
          if (!confirmar) return;

          try {
            const token = localStorage.getItem("token");
            const res = await fetch(`${import.meta.env.VITE_API_BASE}/turnos/${info.event.id}/liberar`, {
              method: "POST",
              headers: {
                Authorization: `Bearer ${token}`,
                "Content-Type": "application/json"
              }
            });

            const data = await res.json();
            if (res.ok) {
              alert("✅ Turno liberado con éxito.");
              const profesorId = document.getElementById("profesorSelect").value;
              const turnos = await getDisponibilidad(profesorId);
              actualizarEventos(turnos);
              clearTurnoTemporal();
            } else {
              alert(`❌ ${data.error || "Error al liberar turno"}`);
            }
          } catch (err) {
            console.error("💥", err);
            alert("❌ No se pudo liberar el turno.");
          }
        });
      }
    },
    eventDidMount: function(info) {
      const esAdmin = localStorage.getItem("es_admin") === "true";
      const estado = info.event.extendedProps.estadoPago;
      if (esAdmin && estado) {
        new bootstrap.Tooltip(info.el, {
          title: `Estado de pago: ${estado}`,
          placement: "top",
          trigger: "hover"
        });
      }
    }
  });

  const esAdmin = localStorage.getItem("es_admin") === "true";
  const leyenda = document.getElementById("barraLeyenda");
  if (leyenda) leyenda.style.display = esAdmin ? "flex" : "none";

  calendar.render();
}

export function actualizarEventos(turnos) {
  if (!calendar) return;
  calendar.removeAllEvents();

  const esAdmin = localStorage.getItem("es_admin") === "true";

  turnos.forEach((turno) => {
    if (!turno.id) return;

    const start = `${turno.fecha}T${turno.hora}`;
    const estado = turno.estado || "";
    const estadoPago = turno.estado_pago || "disponible";

    let backgroundColor = "#198754"; // color por defecto: verde
    let title = estado === "libre" ? "Disponible" : "No disponible";

    if (esAdmin) {
      if (estadoPago === "subido") {
        backgroundColor = "#ffc107"; // 🟡 comprobante subido
        title = "🟡 " + title;
      } else if (estadoPago === "verificado" || estadoPago === "completo") {
        backgroundColor = "#198754"; // ✅ comprobante verificado
        title = "✅ " + title;
      } else if (estado !== "libre") {
        backgroundColor = "#dc3545"; // 🔴 ocupado sin comprobante válido
      }
    } else {
      if (estado !== "libre") {
        backgroundColor = "#dc3545"; // 🔴 para usuarios comunes
      }
    }

    calendar.addEvent({
      id: Number(turno.id),
      title,
      start,
      backgroundColor,
      borderColor: "transparent",
      textColor: "white",
      editable: false,
      extendedProps: {
        estado,
        estadoPago
      }
    });
  });
}

export function marcarTurnoComoOcupado(fecha, hora) {
  const evento = calendar.getEvents().find(e => {
    const d = e.start;
    return (
      d.toISOString().split("T")[0] === fecha &&
      d.toTimeString().slice(0, 5) === hora
    );
  });

  if (evento) {
    evento.setProp("title", "No disponible");
    evento.setProp("backgroundColor", "#dc3545");
    evento.setExtendedProp("estado", "ocupado");
  }
}

export function refrescarSemanaVisible() {
  if (!calendar) return;
  const view = calendar.view;
  const start = view.currentStart.toISOString().split("T")[0];
  const end = view.currentEnd.toISOString().split("T")[0];
  const profesorId = document.getElementById("profesorSelect").value;

  if (!profesorId) {
    console.warn("⚠️ refrescarSemanaVisible: falta profesorId");
    return;
  }

  getDisponibilidad(profesorId, start, end)
    .then((turnos) => {
      actualizarEventos(turnos);
    })
    .catch((err) => {
      console.error("❌ Error al refrescar semana visible:", err);
    });
}