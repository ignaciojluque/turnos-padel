let temporizadorInterval = null;

/**
 * Muestra un mensaje dentro de un elemento
 */
export function mostrarMensaje(elemento, texto, tipo = "info") {
  elemento.textContent = texto;
  elemento.className = `text-${tipo} fw-semibold text-center`;
}

/**
 * Inicia un temporizador regresivo (en segundos) y actualiza el texto
 */
export function iniciarTemporizador(segundos, displayElement, callbackFinal = null, botonDesactivar = null) {
  clearInterval(temporizadorInterval);

  temporizadorInterval = setInterval(() => {
    const min = Math.floor(segundos / 60);
    const seg = segundos % 60;
    displayElement.textContent = `${min.toString().padStart(2, "0")}:${seg.toString().padStart(2, "0")}`;

    if (segundos <= 0) {
      clearInterval(temporizadorInterval);
      displayElement.textContent = "Tiempo agotado";
      if (botonDesactivar) botonDesactivar.disabled = true;
      if (callbackFinal) callbackFinal();
    }

    segundos--;
  }, 1000);
}

/**
 * Vista previa de imagen o PDF cargado
 */
export function mostrarVistaPrevia(inputFile, previewDiv, estadoElemento) {
  const archivo = inputFile.files[0];
  previewDiv.innerHTML = "";

  if (!archivo) return;

  const ext = archivo.name.split(".").pop().toLowerCase();
  if (!["jpg", "jpeg", "png", "webp", "pdf"].includes(ext)) {
    mostrarMensaje(estadoElemento, "Formato no permitido", "danger");
    inputFile.value = "";
    return;
  }

  const reader = new FileReader();
  reader.onload = function (e) {
    if (ext === "pdf") {
      previewDiv.innerHTML = `<p class="text-muted">📄 Archivo PDF seleccionado</p>`;
    } else {
      previewDiv.innerHTML = `<img src="${e.target.result}" class="img-fluid rounded border" style="max-height: 200px;" />`;
    }
  };

  reader.readAsDataURL(archivo);
  estadoElemento.textContent = "";
}

/**
 * Muestra una barra de carga simulada (0% a 100%)
 */
export function simularBarraCarga(barraDiv, barraInterna, callbackFinal = null) {
  barraDiv.style.display = "block";
  let pct = 0;

  const animacion = setInterval(() => {
    pct += 10;
    barraInterna.style.width = `${pct}%`;

    if (pct >= 100) {
      clearInterval(animacion);
      if (callbackFinal) callbackFinal();
    }
  }, 100);
}

export function mostrarSpinner(id = "spinnerLogin") {
  const el = document.getElementById(id);
  if (el) el.classList.remove("d-none");
}

export function ocultarSpinner(id = "spinnerLogin") {
  const el = document.getElementById(id);
  if (el) el.classList.add("d-none");
}


export function poblarSelectProfesores(selectElement, profesores) {
  selectElement.innerHTML = '<option disabled selected value="">-- Seleccioná un profesor --</option>';
  profesores.forEach((profe) => {
    const option = document.createElement("option");
    option.value = profe.id;
    option.textContent = profe.nombre;
    selectElement.appendChild(option);
  });
}
