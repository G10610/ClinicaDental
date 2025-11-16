function horaAMinutos(horaStr) {
    if (!horaStr || !horaStr.includes(':')) {
        console.error("Formato de hora inválido:", horaStr);
        return 0;
    }
    const [h, m] = horaStr.split(":").map(Number);
    return (h * 60) + m;
}

function minutosAHora(totalMinutos) {
    const minNormalizados = Math.min(totalMinutos, 1439);
    const h = Math.floor(minNormalizados / 60).toString().padStart(2, "0");
    const m = Math.round(minNormalizados % 60).toString().padStart(2, "0");
    return `${h}:${m}`;
}

function pintarCita(cita, intervalo) {
    console.log("CITA RECIBIDA EN SEMANAL:", cita);

    const fecha = cita.fecha;
    const duracion = cita.duracion;

    const minutosCita = horaAMinutos(cita.hora);
    const minutosEnSlot = minutosCita % intervalo;
    const minutosSlotInicio = minutosCita - minutosEnSlot;

    const h = Math.floor(minutosSlotInicio / 60).toString().padStart(2, "0");
    const m = (minutosSlotInicio % 60).toString().padStart(2, "0");
    const horaSlot = `${h}:${m}`;

    const celdaContenedora = document.querySelector(
        `.celda-agenda-semanal[data-date="${fecha}"][data-time="${horaSlot}"]`
    );

    if (!celdaContenedora) {
        console.warn("Celda contenedora no encontrada:", { cita, horaSlot });
        return;
    }

    const cssTop = (minutosEnSlot / intervalo) * 100;
    const cssHeight = (duracion / intervalo) * 100;

    const bloque = document.createElement("div");
    bloque.classList.add("cita-block");

    let color = "var(--color-secondary)";
    if (cita.estado === "Confirmada") color = "#1ABC9C";
    if (cita.estado === "Pendiente") color = "#E67E22";
    if (cita.estado === "Cancelada") color = "#E74C3C";
    bloque.style.backgroundColor = color;

    bloque.style.top = `${cssTop}%`;
    bloque.style.height = `calc(${cssHeight}% - 2px)`;

    bloque.innerHTML = `
        <span class="cita-paciente">${cita.paciente_nombre}</span>
        <span class="cita-tratamiento">${cita.tratamiento_nombre}</span>
    `;

    // Menú contextual
    bloque.addEventListener("click", (e) => {
        e.stopPropagation(); 
        console.log("CLICK EN CITA", cita);
        mostrarMenuCita(e, cita);
    });
    celdaContenedora.appendChild(bloque);
}

let menuActual = null;

function mostrarMenuCita(ev, cita) {
    ev.preventDefault();
    ev.stopPropagation();

    const menu = document.getElementById("menu-cita");
    if (!menu) {
        console.error("No existe #menu-cita en el DOM.");
        return;
    }

    menu.innerHTML = `
        <div class="item opcion-menu" data-action="whatsapp"><i class="bi bi-whatsapp me-2" style="color:#25D366"></i>WhatsApp</div>
        <div class="item opcion-menu" data-action="ver"><i class="bi bi-pencil-square me-2"></i>Ver / Editar cita</div>
        <div class="item opcion-menu" data-action="expediente"><i class="bi bi-folder2-open me-2"></i>Ver expediente</div>
        <hr>
        <div class="item opcion-menu" data-action="pendiente">🟧 Marcar Pendiente</div>
        <div class="item opcion-menu" data-action="confirmada">🟩 Marcar Confirmada</div>
        <div class="item opcion-menu" data-action="cancelada">🟥 Marcar Cancelada</div>
    `;

    const pad = 8;
    const menuWidth = 200; 
    const menuHeightEstimate = 220;
    let left = ev.clientX;
    let top = ev.clientY;

    if (left + menuWidth + pad > window.innerWidth) {
        left = window.innerWidth - menuWidth - pad;
    }
    if (top + menuHeightEstimate + pad > window.innerHeight) {
        top = window.innerHeight - menuHeightEstimate - pad;
    }

    menu.style.left = `${left}px`;
    menu.style.top = `${top}px`;
    menu.classList.add('show');

    conectarEventosMenuCita(menu, cita);
    
    setTimeout(() => {
        document.addEventListener('click', cerrarMenuClickFuera);
    }, 0);
}
window.mostrarMenuCita = mostrarMenuCita;


function cerrarMenuClickFuera(e) {
    const menu = document.getElementById("menu-cita");
    if (!menu) return;
    if (!menu.contains(e.target)) {
        menu.classList.remove('show');
        document.removeEventListener('click', cerrarMenuClickFuera);
    }
}

function contactarWhatsapp(telefono) {
    if (!telefono) return alert("El paciente no tiene número registrado.");
    window.open(`https://wa.me/${telefono}`, "_blank");
}

function abrirModalEditar(citaId) {
    if (!urlEditarCitaTemplate) {
        console.error("urlEditarCitaTemplate no definida en el template.");
        alert("No hay URL de edición configurada.");
        return;
    }
    const url = urlEditarCitaTemplate.replace('/0/', `/${citaId}/`);
    const modal = new bootstrap.Modal(document.getElementById('modalEditarCita'));
    const modalBody = document.getElementById('modal-body-form-editar-cita');
    modalBody.innerHTML = `<div class="d-flex justify-content-center align-items-center" style="min-height:200px;"><div class="spinner-border text-primary" role="status"></div></div>`;
    fetch(url)
        .then(r => {
            if (!r.ok) throw new Error('Error cargando datos de la cita');
            return r.text();
        })
        .then(html => {
            modalBody.innerHTML = html;
            const modalFooter = document.querySelector('#modalEditarCita .modal-footer');
            const formButtons = modalBody.querySelector('.modal-footer-contenido');
            if (modalFooter && formButtons) {
                modalFooter.innerHTML = formButtons.innerHTML;
                formButtons.remove();
            }
            if (typeof configurarFormularioCita === 'function') configurarFormularioCita();
            modal.show();
        })
        .catch(err => {
            console.error(err);
            modalBody.innerHTML = `<div class="alert alert-danger">Error al cargar datos.</div>`;
            modal.show();
        });
}

function verExpediente(idPaciente) {
    window.location.href = `/expediente/${idPaciente}`;
}

function cambiarEstado(idCita, nuevoEstado) {
    actualizarEstadoCita(idCita, nuevoEstado);
}


function conectarEventosMenuCita(menu, cita) {
    menu.replaceWith(menu.cloneNode(true));
    const nuevoMenu = document.getElementById("menu-cita");

    nuevoMenu.addEventListener("click", function(ev) {
        ev.stopPropagation();
        const item = ev.target.closest('.opcion-menu');
        if (!item) return;
        const accion = item.dataset.action;
        if (!accion) return;

        if (accion === 'whatsapp') {
            let tel = (cita.paciente_telefono ? String(cita.paciente_telefono) : '').replace(/[^0-9+]/g, '');
            if (tel.startsWith('+')) tel = tel.substring(1);
            if (tel && !tel.startsWith('503')) tel = '503' + tel;
            if (!tel) { alert('Paciente sin teléfono'); nuevoMenu.classList.remove('show'); return; }
            window.open(`https://wa.me/${tel}`, '_blank');
        }

        if (accion === 'ver') {
            abrirModalEditar(cita.id);
        }

        if (accion === 'expediente') {
            const url = urlExpedienteTemplate.replace("0", cita.paciente_id);
            window.open(url, '_blank');
        }

        if (accion === 'pendiente' || accion === 'confirmada' || accion === 'cancelada') {
            const estado = accion === 'pendiente' ? 'Pendiente' : accion === 'confirmada' ? 'Confirmada' : 'Cancelada';
            cambiarEstadoDesdeMenu(cita.id, estado);
        }

        nuevoMenu.classList.remove('show');
    });
}

function getCSRFToken() {
    let csrfToken = null;
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const c = cookie.trim();
        if (c.startsWith('csrftoken=')) {
            csrfToken = c.substring('csrftoken='.length);
            break;
        }
    }
    return csrfToken;
}


function cambiarEstadoDesdeMenu(citaId, nuevoEstado) {

    const csrfToken = getCSRFToken();
    if (!csrfToken) {
        alert("Error de seguridad. No se puede cambiar el estado.");
        return;
    }

    fetch(apiCambiarEstadoURL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            cita_id: citaId,
            nuevo_estado: nuevoEstado
        })
    })
    .then(response => response.json())
    .then(data => {

        if (!data.success) {
            alert("Error: " + (data.error || 'No se pudo cambiar el estado'));
            return;
        }

        const bloque = document.querySelector(`.cita[data-id="${citaId}"]`);
        if (bloque) {
            bloque.classList.remove(
                'cita-pendiente',
                'cita-confirmada',
                'cita-cancelada'
            );

            if (data.nuevo_estado === 'Confirmada') {
                bloque.classList.add('cita-confirmada');
            } else if (data.nuevo_estado === 'Cancelada') {
                bloque.classList.add('cita-cancelada');
            } else {
                bloque.classList.add('cita-pendiente');
            }

            const estadoSpan = bloque.querySelector('.estado-cita');
            if (estadoSpan) estadoSpan.textContent = data.nuevo_estado;
        }

        location.reload();

    })
    .catch(err => {
        console.error("Error en cambiarEstadoDesdeMenu:", err);
        alert("Error de conexión.");
    });
}

// Funciones de fecha
function normalizarHora(hora) {
    if (/^\d{2}:\d{2}$/.test(hora)) {
        return hora;
    }
    const fecha = new Date(`2000-01-01 ${hora}`);
    let h = fecha.getHours().toString().padStart(2, "0");
    let m = fecha.getMinutes().toString().padStart(2, "0");
    return `${h}:${m}`;
}

document.addEventListener('DOMContentLoaded', function () {

    // Elementos DOM
    const fechaInput = document.getElementById('filtro-fecha');
    const fechaLegible = document.getElementById('fecha-legible');
    const prevBtn = document.getElementById('prev-semana');
    const nextBtn = document.getElementById('next-semana');
    const especialistaSelect = document.getElementById('filtro-especialista');
    
    const gridHead = document.querySelector('#agenda-semanal-grid thead');
    const gridBody = document.querySelector('#agenda-semanal-grid tbody');
    
    const modalCrearCita = document.getElementById('modalCrearCita');
    const modalBody = document.getElementById('modal-body-form-cita');

    if (!fechaInput || !fechaLegible || !prevBtn || !nextBtn || !especialistaSelect || !gridBody || !gridHead || !modalCrearCita) {
        console.error('Faltan elementos del DOM en agenda_semanal.js');
        return;
    }

    
    function parseFechaLocal(yyyyMmDd) {
        if (!yyyyMmDd) return new Date();
        const [y, m, d] = yyyyMmDd.split('-').map(Number);
        return new Date(y, m - 1, d);
    }

    function formatearFecha(fecha) {
        const opciones = { day: 'numeric', month: 'long', year: 'numeric' };
        return fecha.toLocaleDateString('es-ES', opciones);
    }

    function getLunes(fecha) {
        const fechaCopia = new Date(fecha.valueOf());
        const diaSemana = fechaCopia.getDay();
        const diff = fechaCopia.getDate() - diaSemana + (diaSemana === 0 ? -6 : 1);
        return new Date(fechaCopia.setDate(diff));
    }

    function formatearRangoFechas(lunes) {
        const dias = gridHead.querySelectorAll('.th-dia-semana').length;
        if (dias === 0) return "Error";

        const fechaFin = new Date(lunes.valueOf());
        fechaFin.setDate(lunes.getDate() + (dias - 1));

        const opcionesInicio = { day: 'numeric', month: 'long' };
        const opcionesFin = { day: 'numeric', month: 'long', year: 'numeric' };

        const inicioStr = lunes.toLocaleDateString('es-ES', opcionesInicio);
        const finStr = fechaFin.toLocaleDateString('es-ES', opcionesFin);

        return `${inicioStr} - ${finStr}`;
    }

    // Lógica de agenda
    function limpiarAgenda() {
        const citasViejas = gridBody.querySelectorAll('.cita-block'); 
        citasViejas.forEach(cita => {
            cita.remove();
        });
    }

    function actualizarInterfazFechas(fechaReferencia) {
        const lunes = getLunes(fechaReferencia);
        
        fechaLegible.textContent = formatearRangoFechas(lunes);

        const ths = gridHead.querySelectorAll('.th-dia-semana');
        const totalDias = ths.length;
        
        for (let i = 0; i < totalDias; i++) {
            const f = new Date(lunes);
            f.setDate(lunes.getDate() + i);
            
            const fechaStr = f.toISOString().split('T')[0];
            const dia = f.toLocaleDateString('es-ES', { weekday:'short' }).replace('.', '');
            const num = f.toLocaleDateString('es-ES', { day:'numeric' });
            
            ths[i].innerHTML = `${dia}<br><span class="fw-normal fs-6">${num}</span>`;
            ths[i].setAttribute('data-date', fechaStr);
        }

        const filas = gridBody.querySelectorAll('tr');
        filas.forEach(fila => {
            const celdas = fila.querySelectorAll('.celda-agenda-semanal');
            for (let i = 0; i < celdas.length; i++) {
                const f = new Date(lunes);
                f.setDate(lunes.getDate() + i);
                celdas[i].setAttribute('data-date', f.toISOString().split('T')[0]);
            }
        });
    }

    function cargarCitas() {
        const especialista_id = especialistaSelect.value;
        const fechaBase = parseFechaLocal(fechaInput.value);
        const lunes = getLunes(fechaBase);
        const fechaInicioSemana = lunes.toISOString().split('T')[0];
        
        limpiarAgenda();

        if (!especialista_id) {
            console.warn("No hay especialista seleccionado.");
            return;
        }

        const url = new URL(apiGetCitasURL, window.location.origin);
        url.searchParams.append('fecha_inicio', fechaInicioSemana);
        url.searchParams.append('especialista_id', especialista_id);
        
        console.log("Cargando citas semanales desde:", url.href);
        
        fetch(url.href)
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
                
                const intervalo = parseInt(gridBody.dataset.intervalo) || 30;
                
                citas.forEach(cita => {
                    pintarCita(cita, intervalo);
                });
            })
            .catch(err => {
                console.error("Error al cargar citas semanales:", err);
            });
    }
    window.cargarCitas = cargarCitas;
    
    function recargarAgendaCompleta() {
        const fechaSeleccionada = parseFechaLocal(fechaInput.value);
        
        actualizarInterfazFechas(fechaSeleccionada);
        
        cargarCitas();
    }


    // Event Listeners
    prevBtn.addEventListener('click', () => {
        const fechaBase = parseFechaLocal(fechaInput.value);
        fechaBase.setDate(fechaBase.getDate() - 7);
        fechaInput.value = fechaBase.toISOString().split('T')[0];
        recargarAgendaCompleta(); 
    });

    nextBtn.addEventListener('click', () => {
        const fechaBase = parseFechaLocal(fechaInput.value);
        fechaBase.setDate(fechaBase.getDate() + 7);
        fechaInput.value = fechaBase.toISOString().split('T')[0];
        recargarAgendaCompleta(); 
    });

    fechaInput.addEventListener('change', () => {
        recargarAgendaCompleta(); 
    });

    especialistaSelect.addEventListener('change', () => {
        const especialistaId = especialistaSelect.value;
        if (especialistaId) {
            localStorage.setItem("especialista_id", especialistaId);
        } else {
            localStorage.removeItem("especialista_id");
        }
        recargarAgendaCompleta(); 
    });

    gridBody.addEventListener('click', function(event) {
        
        const botonEstado = event.target.closest('.btn-cambiar-estado');
        if (botonEstado) {
            event.preventDefault();
            const citaId = botonEstado.dataset.idCita;
            const nuevoEstado = botonEstado.dataset.estado;
            const csrfToken = getCSRFToken();
            if (!csrfToken) return alert("Error de seguridad.");

            fetch(apiCambiarEstadoURL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
                body: JSON.stringify({ 'cita_id': citaId, 'nuevo_estado': nuevoEstado })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    cargarCitas();
                    const popover = bootstrap.Popover.getInstance(document.querySelector('.popover.show'));
                    if (popover) popover.hide();
                } else {
                    alert('Error al actualizar la cita: ' + (data.error || 'Desconocido'));
                }
            })
            .catch(error => console.error('Error en fetch (cambiar estado):', error));
            return;
        }

        const botonWhatsapp = event.target.closest('.cita-whatsapp-btn.disabled');
        if (botonWhatsapp) {
            event.preventDefault();
            console.log("Clic detenido: Teléfono no registrado.");
            return;
        }
    });
    
    gridBody.querySelectorAll('.celda-agenda-semanal').forEach(celda => {
        celda.addEventListener('click', function(e) {
            
            if (e.target.closest('.cita-block')) {
                return;
            }

            const rect = celda.getBoundingClientRect();
            const clickY_relative = e.clientY - rect.top;
            const click_percentage = Math.max(0, clickY_relative / celda.offsetHeight);

            const intervalo = parseInt(gridBody.dataset.intervalo) || 30; 
            const minutosBaseCelda = horaAMinutos(celda.dataset.time); 
            
            let minutosAgregados = 0;

            if (click_percentage >= 0.5) {
                let mitadIntervalo = intervalo / 2; 
                
                const snapping = 5; 
                minutosAgregados = Math.round(mitadIntervalo / snapping) * snapping;
            }

            const minutosTotales = minutosBaseCelda + minutosAgregados;
            
            const horaClicPrecisa = minutosAHora(minutosTotales);
            const fechaClic = celda.dataset.date;
            
            const modal = new bootstrap.Modal(document.getElementById('modalCrearCita'));
            const modalBody = document.getElementById('modal-body-form-cita');
            
            modalBody.innerHTML = `<div class="d-flex justify-content-center align-items-center" style="min-height: 200px;">
                <div class="spinner-border text-primary" role="status"></div>
            </div>`; 

            const especialista_id = especialistaSelect.value;
            
            const urlFormulario = `/citas/crear/?especialista_id=${especialista_id}&fecha=${fechaClic}&hora=${horaClicPrecisa}`;
            
            fetch(urlFormulario)
                .then(response => response.text())
                .then(html => {
                    modalBody.innerHTML = html;
                    
                    const modalFooter = modalCrearCita.querySelector('.modal-footer');
                    const formButtons = modalBody.querySelector('.modal-footer-contenido');

                    
                    if (modalFooter && formButtons) {
                        modalFooter.innerHTML = formButtons.innerHTML;
                        formButtons.remove();
                    }
                    
                    configurarFormularioCita(); 
                })
                .catch(err => {
                    console.error("Error al cargar form modal:", err);
                    modalBody.innerHTML = `<div class="alert alert-danger">Error al cargar.</div>`;
                });

            modal.show();
        });
    });

    function getCSRFToken() {
        let csrfToken = null;
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const cookieLimpia = cookie.trim();
            if (cookieLimpia.startsWith('csrftoken=')) {
                csrfToken = cookieLimpia.substring('csrftoken='.length);
                break;
            }
        }
        if (!csrfToken) console.error("¡Error fatal! No se pudo encontrar el CSRF token.");
        return csrfToken;
    }

    const modalEditarCita = document.getElementById('modalEditarCita');
    if (modalEditarCita) {
        modalEditarCita.addEventListener('show.bs.modal', function (event) {
            const boton = event.relatedTarget;
            const citaId = boton.dataset.idCita;
            const url = urlEditarCitaTemplate.replace('/0/', `/${citaId}/`);
            const modalBody = document.getElementById('modal-body-form-editar-cita');
            
            modalBody.innerHTML = `<div class="d-flex justify-content-center align-items-center" style="min-height: 200px;"><div class="spinner-border text-primary" role="status"></div></div>`;
            
            fetch(url)
                .then(response => response.text())
                .then(html => {
                    modalBody.innerHTML = html;
                    const modalFooter = modalEditarCita.querySelector('.modal-footer');
                    const formButtons = modalBody.querySelector('.modal-footer-contenido');
                    if (modalFooter && formButtons) {
                        modalFooter.innerHTML = formButtons.innerHTML;
                        formButtons.remove();
                    }
                    configurarFormularioCita(); 
                })
                .catch(err => {
                    console.error("Error al cargar form de edición:", err);
                    modalBody.innerHTML = "<div class='alert alert-danger'>Error al cargar los datos.</div>";
                });
        });
    }

    // Carga inicial
    const espGuardado = localStorage.getItem('especialista_id');
    if (espGuardado) {
        especialistaSelect.value = espGuardado;
    }

    recargarAgendaCompleta();

});


// Configuración formulario de cita
function configurarFormularioCita() {
    const input = document.getElementById('buscarPaciente');
    if (!input) {
        console.log("configurarFormularioCita: Saliendo, form no cargado.");
        return; 
    }
    const resultados = document.getElementById('resultadosPacientes');
    const hiddenInput = document.getElementById('paciente_id');
    
    const checkNuevo = document.getElementById('check-nuevo-paciente');
    const contNuevo = document.getElementById('campos-nuevo-paciente');
    const inputNombre = document.getElementById('nuevo_paciente_nombre');
    const inputApellido = document.getElementById('nuevo_paciente_apellido');

    if (!checkNuevo || !contNuevo || !inputNombre || !inputApellido) {
        console.error("Faltan elementos del formulario de nuevo paciente.");
        return; 
    }

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

    checkNuevo.addEventListener('change', function() {
        if (this.checked) {
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
    if(checkNuevo.checked) checkNuevo.dispatchEvent(new Event('change'));

    const duiInput = document.getElementById('id_dui');
    if (duiInput && typeof IMask !== 'undefined') {
        IMask(duiInput, { mask: '00000000-0' });
    } else if (typeof IMask === 'undefined') {
        console.error("IMask.js no se cargó.");
    }

    
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
                    
                    cargarCitas(); 
                    
                } else if (status === 400) {
                    alert(`Error: ${data.error}`); 
                    submitButton.disabled = false;
                    submitButton.innerHTML = 'Guardar Cita';
                } else {
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
        selectTratamiento.dispatchEvent(new Event('change'));
    }

    const btnMenos = document.getElementById('btn-hora-menos');
    const btnMas = document.getElementById('btn-hora-mas');
    const horaText = document.getElementById('hora_text'); 
    const horaHidden = document.getElementById('hora');    

    if (btnMenos && btnMas && horaText && horaHidden) {
        
        const incrementoMinutos = 15; 

        const updateTime = (step) => {
            let currentMinutes = horaAMinutos(horaText.value);
            let newMinutes = currentMinutes + step;
            
            let newHora = minutosAHora(newMinutes);
            
            horaText.value = newHora;
            horaHidden.value = newHora;
        };

        btnMenos.addEventListener('click', () => {
            updateTime(-incrementoMinutos); 
        });

        btnMas.addEventListener('click', () => {
            updateTime(incrementoMinutos); 
        });
    }
}