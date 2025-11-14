document.addEventListener('DOMContentLoaded', function () {


    const fechaInput = document.getElementById('filtro-fecha');
    const fechaLegible = document.getElementById('fecha-legible');
    const prevBtn = document.getElementById('prev-dia');
    const nextBtn = document.getElementById('next-dia');
    const btnDia = document.getElementById('btn-dia');
    const btnSemana = document.getElementById('btn-semana');
    const tituloAgenda = document.getElementById('titulo-agenda');
    const especialistaSelect = document.getElementById('filtro-especialista');
    const tablaCitasBody = document.querySelector('#agenda-table tbody');

    // Seguridad: si falta algo, salimos
    if (!fechaInput || !fechaLegible || !prevBtn || !nextBtn || !especialistaSelect || !tablaCitasBody) {
        console.error('Faltan elementos del DOM en agenda.js');
        return;
    }

    // --- función para parsear fecha YYYY-MM-DD a Date local ---
    function parseFechaLocal(yyyyMmDd) {
        if (!yyyyMmDd) return new Date();
        const [y, m, d] = yyyyMmDd.split('-').map(Number);
        return new Date(y, m - 1, d);
    }

    function formatearFecha(fecha) {
        const opciones = { day: 'numeric', month: 'long', year: 'numeric' };
        return fecha.toLocaleDateString('es-ES', opciones);
    }

    // --- fecha actual (estado) ---
    let fechaActual = parseFechaLocal(fechaInput.value);
    fechaLegible.textContent = formatearFecha(fechaActual);

    function actualizarFechaYRecargar() {
        // Actualiza input y etiqueta
        const yyyyMmDd = fechaActual.toISOString().split('T')[0];
        fechaInput.value = yyyyMmDd;
        fechaLegible.textContent = formatearFecha(fechaActual);
        // Recargar citas para la fecha actual
        cargarCitas();
    }


    // --- 2. FUNCIÓN PRINCIPAL PARA CARGAR CITAS ---
    function cargarCitas() {
        const fecha = fechaInput.value;
        const especialista_id = especialistaSelect.value;

        // Mostrar un 'cargando...' en la tabla
        tablaCitasBody.innerHTML = `<tr><td colspan="5" class="text-center p-4">
            <div class="spinner-border spinner-border-sm text-primary" role="status">
                <span class="visually-hidden">Cargando...</span>
            </div>
            <span class="ms-2">Cargando citas...</span>
        </td></tr>`;

        // Si no hay especialista seleccionado, no buscamos nada
        if (!especialista_id) {
            tablaCitasBody.innerHTML = `<tr><td colspan="5" class="text-center p-4 text-muted">
                Seleccione un especialista para ver la agenda.
            </td></tr>`;
            return;
        }

        // Construir la URL de la API y llamar con fetch
        const url = `/citas/api/get-citas/?fecha=${encodeURIComponent(fecha)}&especialista_id=${encodeURIComponent(especialista_id)}`;
        fetch(url)
            .then(r => {
                if (!r.ok) throw new Error('error en la API');
                return r.json();
            })
            .then(data => {
                tablaCitasBody.innerHTML = '';
                const citas = data.citas || [];

                if (!Array.isArray(citas) || citas.length === 0) {
                    tablaCitasBody.innerHTML = `<tr><td colspan="5" class="text-center p-4 text-muted">No hay citas programadas para este día.</td></tr>`;
                    return;
                }

                citas.forEach(cita => {
                    let estadoClass = 'text-bg-secondary';
                    if (cita.estado === 'Confirmada') estadoClass = 'text-bg-success';
                    if (cita.estado === 'Cancelada') estadoClass = 'text-bg-danger';

                    const filaHTML = `
                        <tr>
                            <td class="cell-hora fw-bold">${cita.hora}</td>
                            <td class="cell-paciente">${cita.paciente_nombre}</td>
                            <td class="cell-tratamiento">${cita.tratamiento_nombre}</td>
                            <td><span class="badge ${estadoClass}">${cita.estado}</span></td>
                            <td class="text-center">
                                <a href="#" class="btn btn-sm btn-ver">Ver</a>
                                <a href="#" class="btn btn-sm btn-borrar">X</a>
                            </td>
                        </tr>
                    `;
                    tablaCitasBody.innerHTML += filaHTML;
                });
            })
            .catch(err => {
                console.error("Error al cargar citas:", err);
                tablaCitasBody.innerHTML = `<tr><td colspan="5" class="text-center p-4 text-danger">Error al cargar la agenda. Intente de nuevo.</td></tr>`;
            });
    }


    // Navegación por días
    prevBtn.addEventListener('click', () => {
        fechaActual.setDate(fechaActual.getDate() - 1);
        actualizarFechaYRecargar();
    });

    nextBtn.addEventListener('click', () => {
        fechaActual.setDate(fechaActual.getDate() + 1);
        actualizarFechaYRecargar();
    });

    fechaInput.addEventListener('change', () => {
        fechaActual = parseFechaLocal(fechaInput.value);
        actualizarFechaYRecargar();
    });

    // Cambiar entre vista Día / Semana
    if (btnDia && btnSemana && tituloAgenda) {
    btnDia.addEventListener('click', () => {
        btnDia.classList.add('active');
        btnSemana.classList.remove('active');
        tituloAgenda.textContent = 'Agenda diaria';
    });

    btnSemana.addEventListener('click', () => {
        btnSemana.classList.add('active');
        btnDia.classList.remove('active');
        tituloAgenda.textContent = 'Agenda semanal';
    });
    }

   
    // ¡Nuevo listener para el especialista!
    especialistaSelect.addEventListener('change', () => {
        cargarCitas();
    });
    
    // --- 5. CARGA INICIAL ---
    // Carga las citas la primera vez que la página abre
    const espGuardado = localStorage.getItem('especialista_id');
    if (espGuardado) especialistaSelect.value = espGuardado;
    
    cargarCitas();

// === 2.(MANEJO DEL MODAL "CREAR CITA") ===

    let filtroEspecialista = document.getElementById('filtro-especialista').value;
    if (!filtroEspecialista) {
        filtroEspecialista = localStorage.getItem('especialista_id') || '';
    }
    
    const modalCrearCita = document.getElementById('modalCrearCita');
    const modalBody = document.getElementById('modal-body-form-cita');
    
    // 1. Escuchar cuando el modal esté a punto de abrirse
    //    (Añado un 'if' por seguridad, por si el modal no existiera en otra página)
    
    if (modalCrearCita) {
        modalCrearCita.addEventListener('show.bs.modal', function (event) {
            const filtroEspecialista = especialistaSelect.value;
            const filtroFecha = fechaInput.value;

            modalBody.innerHTML = `...spinner...`;

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
                    // Asumiendo que tienes una función para inicializar form y validaciones
                    if (typeof configurarFormularioCita === 'function') configurarFormularioCita();
                })
                .catch(error => {
                    console.error('Error:', error);
                    modalBody.innerHTML = `<div class="alert alert-danger">Error al cargar. Por favor, intenta de nuevo.</div>`;
                });
        });
    }

}); 


// en static/js/agenda.js

function configurarFormularioCita() {
    // --- 1. Definir todos los elementos ---
    const input = document.getElementById('buscarPaciente');
    if (!input) return; // Seguridad
    const resultados = document.getElementById('resultadosPacientes');
    const hiddenInput = document.getElementById('paciente_id');
    
    // Elementos del formulario de nuevo paciente
    const checkNuevo = document.getElementById('check-nuevo-paciente');
    const contNuevo = document.getElementById('campos-nuevo-paciente');
    const inputNombre = document.getElementById('nuevo_paciente_nombre');
    const inputApellido = document.getElementById('nuevo_paciente_apellido');

    // Check de seguridad
    if (!checkNuevo || !contNuevo || !inputNombre || !inputApellido) {
        console.error("Faltan elementos del formulario de nuevo paciente.");
        return; 
    }

    // --- 2. Lógica de Búsqueda (KEYUP) ---
    input.addEventListener('keyup', function() {
        // Guard clause si está deshabilitado
        if (input.disabled) { 
            resultados.innerHTML = '';
            return;
        }
        
        const query = input.value.trim();
        if (query.length < 2) {
            resultados.innerHTML = '';
            return;
        }

        // Fetch
        fetch(`${buscarPacientesURL}?q=${encodeURIComponent(query)}`)
            .then(res => res.json())
            .then(data => {
                resultados.innerHTML = ''; // Limpiar
                
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
                // --- FIN DE LA PARTE RESTAURADA ---
            })
            .catch(error => {
                console.error('Error en fetch buscar_pacientes:', error);
                resultados.innerHTML = '<div class="list-group-item text-danger">Error al buscar</div>';
            });
    });

    // --- 3. Lógica del Checkbox (CHANGE) ---
    // (Esta parte ya te funcionaba bien)
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

    // --- 4. ACTIVAR LA MÁSCARA DEL DUI ---
    // (Esto reemplaza el script que borraste de form_cita.html)
    const duiInput = document.getElementById('id_dui');
    if (duiInput && typeof IMask !== 'undefined') {
        IMask(duiInput, { mask: '00000000-0' });
    } else if (typeof IMask === 'undefined') {
        console.error("IMask.js no se cargó. Revisa agenda.html");
    }

    
    // --- 5. MANEJAR EL ENVÍO (SUBMIT) DEL FORMULARIO ---
    const form = document.getElementById('form-crear-cita');
    const modalBody = document.getElementById('modal-body-form-cita');

    if (form) {
        form.addEventListener('submit', function(event) {
            // ¡Prevenir el envío normal!
            event.preventDefault(); 
            
            // (Opcional) Mostrar un spinner en el botón de guardar
            const submitButton = modalCrearCita.querySelector('button[type="submit"]');
            submitButton.disabled = true;
            submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Guardando...';

            const formData = new FormData(form);

            fetch(form.action, { // form.action viene de tu HTML: {% url 'crear_cita' %}
                method: 'POST',
                body: formData,
                headers: {
                    // Django necesita esto para AJAX POST
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken') 
                }
            })
            .then(response => {
                // Pedimos la respuesta en JSON
                return response.json().then(data => ({ ok: response.ok, status: response.status, data }));
            })
            .then(({ ok, status, data }) => {
                if (ok) {
                    // ¡Éxito! (Status 200)
                    const modal = bootstrap.Modal.getInstance(document.getElementById('modalCrearCita'));
                    modal.hide();
                    window.location.reload(); // Recarga la página de la agenda
                    
                } else if (status === 400) {
                    // ¡Error de Validación! (Status 400)
                    // 'data.error' es el mensaje que enviaste desde views.py
                    alert(`Error: ${data.error}`); // Muestra el error
                    submitButton.disabled = false;
                    submitButton.innerHTML = 'Guardar Cita';
                } else {
                    // Otro error (ej. 500)
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


    const selectTratamiento = document.getElementById('tratamiento');
    const duracionSpan = document.getElementById('duracion-minutos');

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


}



