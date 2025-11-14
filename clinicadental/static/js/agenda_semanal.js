document.addEventListener('DOMContentLoaded', function () {

    // --- NUEVO ---
    // Construye la cuadrícula con las fechas de la semana actual
    function reconstruirTablaSemana(lunes) {

        // 1) Calcular las fechas 
        const fechasSemana = [];
        for (let i = 0; i < totalDias; i++) {
            const f = new Date(lunes);
            f.setDate(lunes.getDate() + i);
            fechasSemana.push(f);
        }

        // 2) Actualizar ENCABEZADOS (th)
        const ths = document.querySelectorAll('.th-dia-semana');
        fechasSemana.forEach((f, index) => {
            const fechaStr = f.toISOString().split('T')[0];
            const legible = f.toLocaleDateString('es-ES', { weekday:'short', day:'numeric' });
            ths[index].textContent = legible;
            ths[index].setAttribute('data-date', fechaStr);
        });

        // 3) Actualizar cada FILA de horas
        const filas = gridBody.querySelectorAll('tr');
        filas.forEach(fila => {
            const hora = fila.getAttribute('data-time'); // "08:00", "09:00", etc.

            const celdas = fila.querySelectorAll('.celda-agenda-semanal');

            celdas.forEach((celda, idx) => {
                const fechaStr = fechasSemana[idx].toISOString().split('T')[0];

                // Reasignar la fecha correcta
                celda.setAttribute('data-date', fechaStr);

                // LIMPIAR citas antiguas
                const eventos = celda.querySelectorAll('.cita-evento');
                eventos.forEach(ev => ev.remove());
            });
        });
    }
    
    // --- 1. ELEMENTOS DEL DOM ---
    // (Casi todos son iguales a agenda.js)
    const fechaInput = document.getElementById('filtro-fecha');
    const fechaLegible = document.getElementById('fecha-legible');
    const prevBtn = document.getElementById('prev-semana');
    const nextBtn = document.getElementById('next-semana');
    const especialistaSelect = document.getElementById('filtro-especialista');

    // Detectar cuántos días hay en la tabla horizontal
    const totalDias = document.querySelectorAll('.th-dia-semana').length;
    
    // ¡IMPORTANTE! Elemento de la cuadrícula
    const gridBody = document.querySelector('#agenda-semanal-grid tbody');
    
    const modalCrearCita = document.getElementById('modalCrearCita');
    const modalBody = document.getElementById('modal-body-form-cita');

    // Seguridad: si falta algo, salimos
    if (!fechaInput || !fechaLegible || !prevBtn || !nextBtn || !especialistaSelect || !gridBody || !modalCrearCita) {
        console.error('Faltan elementos del DOM en agenda_semanal.js');
        return;
    }

    function normalizarHora(hora) {
        // Si ya viene en formato "HH:MM", lo dejamos igual
        if (/^\d{2}:\d{2}$/.test(hora)) {
            return hora;
        }

        // Si viene en formato "HH:MM AM/PM"
        const fecha = new Date(`2000-01-01 ${hora}`);
        let h = fecha.getHours().toString().padStart(2, "0");
        let m = fecha.getMinutes().toString().padStart(2, "0");
        return `${h}:${m}`;
    }


    // --- 2. FUNCIONES DE FECHA ---
    // (parseFechaLocal y formatearFecha son copiadas de agenda.js)
    function parseFechaLocal(yyyyMmDd) {
        if (!yyyyMmDd) return new Date();
        const [y, m, d] = yyyyMmDd.split('-').map(Number);
        return new Date(y, m - 1, d);
    }

    function formatearFecha(fecha) {
        const opciones = { day: 'numeric', month: 'long', year: 'numeric' };
        return fecha.toLocaleDateString('es-ES', opciones);
    }

    // --- NUEVA FUNCIÓN ---
    // Obtiene el lunes de la semana de una fecha dada
    function getLunes(fecha) {
        const fechaCopia = new Date(fecha.valueOf());
        const diaSemana = fechaCopia.getDay(); // Domingo = 0, Lunes = 1, ...
        const diff = fechaCopia.getDate() - diaSemana + (diaSemana === 0 ? -6 : 1); // Ajuste para que Lunes sea el primero
        return new Date(fechaCopia.setDate(diff));
    }

    // --- NUEVA FUNCIÓN ---
    // Formatea el rango de la etiqueta (ej: "10 nov - 16 nov, 2025")
    function formatearRangoFechas(lunes) {
        // Número real de columnas de la tabla
        const dias = document.querySelectorAll('.th-dia-semana').length;

        const fechaFin = new Date(lunes.valueOf());
        fechaFin.setDate(lunes.getDate() + (dias - 1));

        const opcionesInicio = { day: 'numeric', month: 'long' };
        const opcionesFin = { day: 'numeric', month: 'long', year: 'numeric' };

        const inicioStr = lunes.toLocaleDateString('es-ES', opcionesInicio);
        const finStr = fechaFin.toLocaleDateString('es-ES', opcionesFin);

        return `${inicioStr} - ${finStr}`;
    }



    // --- 3. ESTADO Y NAVEGACIÓN ---
    
    // 'fechaActual' es la fecha del input, la usamos como referencia
    let fechaActual = parseFechaLocal(fechaInput.value);
    
    // La etiqueta legible muestra el rango semanal
    fechaLegible.textContent = formatearRangoFechas(getLunes(fechaActual));

    function actualizarFechaYRecargar() {
        // 1) deja que el input sea la verdad absoluta
        const fechaSeleccionada = parseFechaLocal(fechaInput.value);

        // 2) calcula lunes basándote en ESA fecha (no en fechaActual)
        const lunes = getLunes(fechaSeleccionada);

        // 3) reconstruir tabla
        reconstruirTablaSemana(lunes);

        // 4) actualizar etiqueta
        fechaLegible.textContent = formatearRangoFechas(lunes);

        // 5) cargar citas
        cargarCitas();
    }


    prevBtn.addEventListener('click', () => {
        const fechaBase = parseFechaLocal(fechaInput.value);
        fechaBase.setDate(fechaBase.getDate() - 7);
        fechaInput.value = fechaBase.toISOString().split('T')[0];
        actualizarFechaYRecargar();

    });


    nextBtn.addEventListener('click', () => {
        const fechaBase = parseFechaLocal(fechaInput.value);
        fechaBase.setDate(fechaBase.getDate() + 7);
        fechaInput.value = fechaBase.toISOString().split('T')[0];
        actualizarFechaYRecargar();

    });

    fechaInput.addEventListener('change', () => {
        const nuevaFecha = fechaInput.value;
        if (nuevaFecha) {
            fechaActual = parseFechaLocal(nuevaFecha);
            actualizarFechaYRecargar(); // ← FIX REAL
        }
    });

    

// En agenda_semanal.js, REEMPLAZA tu listener de especialistaSelect

    especialistaSelect.addEventListener('change', () => {
        // (Este ya estaba bien)
        const especialistaId = especialistaSelect.value;
        
        if (especialistaId) {
            localStorage.setItem("especialista_id", especialistaId);
        } else {
            localStorage.removeItem("especialista_id");
        }
        
        recargarSemanaConFecha(fechaInput.value, especialistaId);
    });

    // --- 4. FUNCIÓN PRINCIPAL PARA CARGAR CITAS ---
    // (Esta es tu función esqueleto, pero adaptada para llamar a la API correcta)
    function cargarCitas() {
        const especialista_id = especialistaSelect.value;

        // Limpiar todas las citas anteriores de la cuadrícula
        gridBody.querySelectorAll('.cita-evento').forEach(citaEl => citaEl.remove());

        if (!especialista_id) {
            console.warn("No hay especialista seleccionado.");
            // (Opcional: mostrar un mensaje en la UI)
            return;
        }

        // --- ADAPTADO ---
        // 1. Calcular el lunes de la semana actual
        const lunes = getLunes(parseFechaLocal(fechaInput.value));
        const fechaInicioSemana = lunes.toISOString().split('T')[0];

        // 2. Construir la URL para la NUEVA API SEMANAL
        // Asumimos que la URL en el HTML se llama 'apiGetCitasURL'
        // y que tu nueva API acepta `fecha_inicio`
        const url = `${apiGetCitasURL}?fecha_inicio=${fechaInicioSemana}&especialista_id=${especialista_id}`;
        
        console.log("Cargando citas semanales desde:", url);

        fetch(url)
            .then(r => {
                if (!r.ok) throw new Error('Error en la API semanal');
                return r.json();
            })
            .then(data => {
                const citas = data.citas || [];

                if (citas.length === 0) {
                    console.log("No hay citas para esta semana.");
                    return;
                }

                citas.forEach(cita => {

                    // 1. VARIABLES REALES QUE SÍ EXISTEN
                    const fecha = cita.fecha;         // YYYY-MM-DD
                    const hora = cita.hora;           // "08:00" o "08:00 AM"
                    
                    const horaNormalizada = normalizarHora(hora);

                    // 2. BUSCAR LA CELDA CORRECTA EN LA TABLA
                    const celda = document.querySelector(
                        `.celda-agenda-semanal[data-date="${fecha}"][data-time="${horaNormalizada}"]`
                    );

                    if (!celda) {
                        console.warn("No se encontró celda para:", fecha, horaNormalizada);
                        return;
                    }

                    // 3. RENDERIZAR EVENTO
                    const citaDiv = document.createElement('div');
                    citaDiv.className = 'cita-evento';

                    // Colores por estado
                    let estadoClass = 'bg-secondary';
                    if (cita.estado === 'Confirmada') estadoClass = 'bg-success';
                    if (cita.estado === 'Cancelada') estadoClass = 'bg-danger';
                    citaDiv.classList.add(estadoClass);

                    citaDiv.innerHTML = `
                        <strong class="cita-paciente">${cita.paciente_nombre}</strong>
                        <span class="cita-tratamiento">${cita.tratamiento_nombre}</span>
                    `;

                    celda.appendChild(citaDiv);
                });

            })
            .catch(err => {
                console.error("Error al cargar citas semanales:", err);
            });
    }
    
    window.cargarCitas = cargarCitas;

    // --- 5. MANEJO DEL MODAL ---
    
    // --- NUEVO ---
    // Esta es tu lógica del esqueleto para abrir el modal AL HACER CLIC EN UNA CELDA
    // (Está perfecta como la tenías)
    gridBody.querySelectorAll('.celda-agenda-semanal').forEach(celda => {
        celda.addEventListener('click', function(e) {
            
            if (e.target.closest('.cita-evento')) {
                // (Futuro) Aquí abrirías el modal de "Ver/Editar"
                console.log("Clic en una cita existente");
                return;
            }

            // Es una celda vacía, abrir modal de CREAR
            const fechaClic = celda.dataset.date;
            const horaClic = celda.dataset.time;
            
            const modal = new bootstrap.Modal(document.getElementById('modalCrearCita'));
            const modalBody = document.getElementById('modal-body-form-cita');
            
            modalBody.innerHTML = `<div class="d-flex justify-content-center align-items-center" style="min-height: 200px;">
                <div class="spinner-border text-primary" role="status"></div>
            </div>`; // Spinner

            const especialista_id = especialistaSelect.value;
            // IMPORTANTE: Esta URL debe apuntar a la vista que renderiza el *formulario*
            const urlFormulario = `/citas/crear/?especialista_id=${especialista_id}&fecha=${fechaClic}&hora=${horaClic}`;
            
            fetch(urlFormulario)
                .then(response => response.text())
                .then(html => {
                    modalBody.innerHTML = html;
                    
                    // Mover botones del footer (lógica copiada de agenda.js)
                    const modalFooter = modalCrearCita.querySelector('.modal-footer');
                    const formButtons = modalBody.querySelector('.modal-footer-contenido');
                    const selectHora = modalBody.querySelector('#hora');
                    
                    if (selectHora) {
                        selectHora.value = horaClic; 
                    }
                    if (modalFooter && formButtons) {
                        modalFooter.innerHTML = formButtons.innerHTML;
                        formButtons.remove();
                    }
                    
                    configurarFormularioCita(); // ¡Configurar el form recién cargado!
                })
                .catch(err => {
                    console.error("Error al cargar form modal:", err);
                    modalBody.innerHTML = `<div class="alert alert-danger">Error al cargar.</div>`;
                });

            modal.show();
        });
    });

    // --- COPIADO DE agenda.js ---
    // Esta lógica es para abrir el modal con el BOTÓN "NUEVA CITA"
    // (Usa la fecha del input, sin hora específica)
    if (modalCrearCita) {
        modalCrearCita.addEventListener('show.bs.modal', function (event) {
            
            // IMPORTANTE: Solo ejecutar si se abrió con el botón (relatedTarget)
            // Si no, la lógica de 'clic en celda' ya se encargó.
            if (!event.relatedTarget) {
                return; 
            }

            const filtroEspecialista = especialistaSelect.value;
            const filtroFecha = fechaInput.value; // Usa la fecha del input

            modalBody.innerHTML = `<div class="d-flex justify-content-center align-items-center" style="min-height: 200px;">
                <div class="spinner-border text-primary" role="status"></div>
            </div>`; // Spinner

            // Esta URL no pasa la hora, el form usará la primera disponible
            const url = `/citas/crear/?especialista_id=${filtroEspecialista}&fecha=${filtroFecha}`;
            
            fetch(url)
                .then(response => {
                    if (!response.ok) throw new Error('Error al cargar el formulario.');
                    return response.text();
                })
                .then(html => {
                    modalBody.innerHTML = html;
                    const modalFooter = modalCrearCita.querySelector('.modal-footer');
                    const formButtons = modalBody.querySelector('.modal-footer-contenido');
                    if (modalFooter && formButtons) {
                        modalFooter.innerHTML = formButtons.innerHTML;
                        formButtons.remove();
                    }
                    if (typeof configurarFormularioCita === 'function') configurarFormularioCita();
                })
                .catch(error => {
                    console.error('Error:', error);
                    modalBody.innerHTML = `<div class="alert alert-danger">Error al cargar. Por favor, intenta de nuevo.</div>`;
                });
        });
    }

    // --- 6. CARGA INICIAL ---
    // (Copiado de agenda.js)
    const espGuardado = localStorage.getItem('especialista_id');
    if (espGuardado && espGuardado !== especialistaSelect.value) {
         // Si localStorage tiene un ID pero la URL no (ej. al cargar por primera vez)
         // O si el ID de la URL es diferente, forzamos la recarga para sincronizar.
         console.log("Sincronizando especialista de localStorage...");
         recargarSemanaConFecha(fechaInput.value, espGuardado);
    } else {
        // Si todo está sincronizado, simplemente cargamos las citas
        cargarCitas();
    }

    function recargarSemanaConFecha(yyyyMmDd, especialistaId) {
        // 1. Actualizar estado interno
        fechaActual = parseFechaLocal(yyyyMmDd);

        // 2. Actualizar input
        fechaInput.value = yyyyMmDd;

        // 3. Actualizar el rango legible
        fechaLegible.textContent = formatearRangoFechas(getLunes(fechaActual));

        // 4. Actualizar especialista si viene
        if (especialistaId) {
            especialistaSelect.value = especialistaId;
        }

        // 5. Cargar citas correctamente
        cargarCitas();
    }

});


// === 7. FUNCIÓN DE CONFIGURACIÓN DEL FORMULARIO ===
// (Esta función es COPIADA ÍNTEGRAMENTE de agenda.js)
// (Asegúrate de que 'buscarPacientesURL' esté definida en tu HTML)

function configurarFormularioCita() {
    // --- 1. Definir todos los elementos ---
    const input = document.getElementById('buscarPaciente');
    if (!input) {
        console.log("configurarFormularioCita: Saliendo, form no cargado.");
        return; // Seguridad
    }
    const resultados = document.getElementById('resultadosPacientes');
    const hiddenInput = document.getElementById('paciente_id');
    
    // ... (resto de 'const' de agenda.js) ...
    const checkNuevo = document.getElementById('check-nuevo-paciente');
    const contNuevo = document.getElementById('campos-nuevo-paciente');
    const inputNombre = document.getElementById('nuevo_paciente_nombre');
    const inputApellido = document.getElementById('nuevo_paciente_apellido');

    if (!checkNuevo || !contNuevo || !inputNombre || !inputApellido) {
        console.error("Faltan elementos del formulario de nuevo paciente.");
        return; 
    }

    // --- 2. Lógica de Búsqueda (KEYUP) ---
    input.addEventListener('keyup', function() {
        if (input.disabled) { 
            resultados.innerHTML = '';
            return;
        }
        
        const query = input.value.trim();
        if (query.length < 2) {
            resultados.innerHTML = '';
            return;
        }

        fetch(`${buscarPacientesURL}?q=${encodeURIComponent(query)}`)
            .then(res => res.json())
            .then(data => {
                resultados.innerHTML = ''; 
                
                if (data.length === 0) {
                    resultados.innerHTML = '<div class="list-group-item text-muted">Sin coincidencias</div>';
                    return;
                }

                data.forEach(p => {
                    const item = document.createElement('a');
                    item.className = 'list-group-item list-group-item-action';
                    item.href = "#";
                    item.innerHTML = `
                        <strong>${p.nombre} ${p.apellido}</strong> 
                        <small class="text-muted">(${p.telefono || 'Sin teléfono'})</small>
                    `;
                    
                    item.addEventListener('click', (e) => {
                        e.preventDefault();
                        input.value = `${p.nombre} ${p.apellido}`;
                        hiddenInput.value = p.id;
                        resultados.innerHTML = '';
                    });
                    resultados.appendChild(item);
                });
            })
            .catch(error => {
                console.error('Error en fetch buscar_pacientes:', error);
                resultados.innerHTML = '<div class="list-group-item text-danger">Error al buscar</div>';
            });
    });

    // --- 3. Lógica del Checkbox (CHANGE) ---
    checkNuevo.addEventListener('change', function() {
        if (this.checked) {
            // Modo "NUEVO PACIENTE"
            input.disabled = true;
            input.classList.add('bg-light');
            input.value = '';
            resultados.innerHTML = ''; 
            hiddenInput.value = '';     
            contNuevo.style.display = 'flex';
            hiddenInput.required = false; 
            inputNombre.required = true;
            inputApellido.required = true;
        } else {
            // Modo "BUSCAR PACIENTE"
            input.disabled = false;
            input.classList.remove('bg-light');
            contNuevo.style.display = 'none';   
            hiddenInput.required = true; 
            inputNombre.required = false; 
            inputApellido.required = false;
            inputNombre.value = ''; 
            inputApellido.value = '';
        }
    });
    // Trigger 'change' en caso de que el form venga pre-marcado
    if(checkNuevo.checked) checkNuevo.dispatchEvent(new Event('change'));

    // --- 4. ACTIVAR LA MÁSCARA DEL DUI ---
    const duiInput = document.getElementById('id_dui');
    if (duiInput && typeof IMask !== 'undefined') {
        IMask(duiInput, { mask: '00000000-0' });
    } else if (typeof IMask === 'undefined') {
        console.error("IMask.js no se cargó.");
    }

    
    // --- 5. MANEJAR EL ENVÍO (SUBMIT) DEL FORMULARIO ---
    const form = document.getElementById('form-crear-cita');
    
    if (form) {
        form.addEventListener('submit', function(event) {
            event.preventDefault(); 
            
            const submitButton = document.querySelector('#modalCrearCita .modal-footer button[type="submit"]');
            submitButton.disabled = true;
            submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Guardando...';

            const formData = new FormData(form);

            fetch(form.action, { 
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken') 
                }
            })
            .then(response => {
                return response.json().then(data => ({ ok: response.ok, status: response.status, data }));
            })
            .then(({ ok, status, data }) => {
                if (ok) {
                    const modal = bootstrap.Modal.getInstance(document.getElementById('modalCrearCita'));
                    modal.hide();
                    
                    // En lugar de recargar toda la página, solo recargamos las citas
                    cargarCitas(); 


                    
                } else if (status === 400) {
                    // Error de Validación
                    alert(`Error: ${data.error}`); // Muestra el error
                    submitButton.disabled = false;
                    submitButton.innerHTML = 'Guardar Cita';
                } else {
                    // Otro error
                    throw new Error(data.error || 'Error del servidor.');
                }
            })
            .catch(error => {
                console.error('Error al enviar el formulario:', error);
                alert('Ocurrió un error inesperado. Por favor, intente de nuevo.');
                submitButton.disabled = false;
                submitButton.innerHTML = 'Guardar Cita';
            });
        });
    }

    // --- 6. LÓGICA DE DURACIÓN DEL TRATAMIENTO ---
    const selectTratamiento = document.getElementById('tratamiento');
    const duracionSpan = document.getElementById('duracion-minutos');

    if (selectTratamiento && duracionSpan) {
        selectTratamiento.addEventListener('change', function() {
            const duracion = parseInt(this.selectedOptions[0].dataset.duracion);
        
            if (isNaN(duracion) || duracion <= 0) {
                duracionSpan.textContent = '—';
                return;
            }
        
            const horas = Math.floor(duracion / 60);
            const minutos = duracion % 60;
        
            let texto = '';
            if (horas > 0) {
                texto += horas === 1 ? '1 hora' : `${horas} horas`;
            }
            if (minutos > 0) {
                texto += horas > 0 ? ' y ' : '';
                texto += `${minutos} minutos`;
            }
        
            duracionSpan.textContent = texto;
        });
        // Trigger para que se ejecute al cargar el modal
        selectTratamiento.dispatchEvent(new Event('change'));
    }
}



