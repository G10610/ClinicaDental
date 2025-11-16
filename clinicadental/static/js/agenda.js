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

    if (!fechaInput || !fechaLegible || !prevBtn || !nextBtn || !especialistaSelect || !tablaCitasBody) {
        console.error('Faltan elementos del DOM en agenda.js');
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

    let fechaActual = parseFechaLocal(fechaInput.value);
    fechaLegible.textContent = formatearFecha(fechaActual);

    function actualizarFechaYRecargar() {
        const yyyyMmDd = fechaActual.toISOString().split('T')[0];
        fechaInput.value = yyyyMmDd;
        fechaLegible.textContent = formatearFecha(fechaActual);
        cargarCitas();
    }

    function cargarCitas() {
        const fecha = fechaInput.value;
        const especialista_id = especialistaSelect.value;

        tablaCitasBody.innerHTML = `<tr><td colspan="5" class="text-center p-4">
            <div class="spinner-border spinner-border-sm text-primary" role="status">
                <span class="visually-hidden">Cargando...</span>
            </div>
            <span class="ms-2">Cargando citas...</span>
        </td></tr>`;

        if (!especialista_id) {
            tablaCitasBody.innerHTML = `<tr><td colspan="5" class="text-center p-4 text-muted">
                Seleccione un especialista para ver la agenda.
            </td></tr>`;
            return;
        }

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

                    let telLimpio = '';
                    if (cita.paciente_telefono) {
                        telLimpio = cita.paciente_telefono.replace(/[^0-9+]/g, '');

                        if (telLimpio.startsWith('+')) {
                            telLimpio = telLimpio.substring(1);
                        }
                    }

                    if (telLimpio.length > 0) {
                        if (!telLimpio.startsWith('503')) {
                            telLimpio = `503${telLimpio}`;
                        }
                    }

                    const esClickeable = telLimpio ? true : false;
                    const whatsappLink = esClickeable ? `https://wa.me/${telLimpio}` : '#';
                    const targetBlank = esClickeable ? 'target="_blank"' : '';
                    const claseDisabled = esClickeable ? '' : 'disabled';
                    const title = esClickeable ? 'Enviar WhatsApp' : 'Teléfono no registrado';

                    const urlExpediente = urlExpedienteTemplate.replace('/0/', `/${cita.paciente_id}/`);

                   const filaHTML = `
                    <tr>
                        <td class="cell-hora fw-bold">${cita.hora}</td>
                        
                        <td class="cell-paciente">${cita.paciente_nombre}</td>
                        
                        <td class="cell-tratamiento">${cita.tratamiento_nombre}</td>
                        
                        <td><span class="badge ${estadoClass}">${cita.estado}</span></td>
                        
                        <td class="text-center">
                            <div class="d-flex justify-content-center gap-2">

                                <a href="${whatsappLink}" ${targetBlank}
                                   class="btn btn-accion-agenda btn-accion-whatsapp ${claseDisabled}"
                                   title="${title}">
                                    <i class="bi bi-whatsapp"></i>
                                </a>

                                <button type="button" 
                                    class="btn btn-accion-agenda btn-accion-editar" 
                                    title="Ver/Editar Cita"
                                    data-bs-toggle="modal" 
                                    data-bs-target="#modalEditarCita" 
                                    data-id-cita="${cita.id}">
                                    <i class="bi bi-eye-fill"></i>
                                </button>
                                
                                <a href="${urlExpediente}" 
                                   class="btn btn-accion-agenda btn-accion-expediente"
                                   title="Ver Expediente">
                                    <i class="bi bi-folder-fill"></i>
                                </a>

                                <div class="dropdown" data-bs-container="body">
                                    <button class="btn btn-accion-agenda btn-accion-menu dropdown-toggle" 
                                            type="button" 
                                            data-bs-toggle="dropdown" 
                                            aria-expanded="false"
                                            title="Cambiar Estado"
                                            data-bs-strategy="fixed" >
                                        <i class="bi bi-three-dots-vertical"></i>
                                    </button>
                                    <ul class="dropdown-menu dropdown-menu-end">
                                        <li>
                                            <a class="dropdown-item dropdown-item-estado btn-cambiar-estado" href="#" 
                                               data-id-cita="${cita.id}" data-estado="Pendiente">
                                                <i class="bi bi-clock-history text-warning"></i> Pendiente
                                            </a>
                                        </li>
                                        <li>
                                            <a class="dropdown-item dropdown-item-estado btn-cambiar-estado" href="#" 
                                               data-id-cita="${cita.id}" data-estado="Confirmada">
                                                <i class="bi bi-check-circle-fill text-success"></i> Confirmada
                                            </a>
                                        </li>
                                        <li>
                                            <a class="dropdown-item dropdown-item-estado btn-cambiar-estado" href="#" 
                                               data-id-cita="${cita.id}" data-estado="Cancelada">
                                                <i class="bi bi-x-circle-fill text-danger"></i> Cancelada
                                            </a>
                                        </li>
                                    </ul>
                                </div>

                            </div>
                        </td>
                    </tr>
                `;
                    tablaCitasBody.innerHTML += filaHTML;
                });
                
                setTimeout(() => {
                    document.querySelectorAll('.dropdown-toggle').forEach(el => {
                        new bootstrap.Dropdown(el, {
                            popperConfig: {
                                strategy: "fixed"
                            }
                        });
                    });
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

    
    especialistaSelect.addEventListener('change', () => {
        cargarCitas();
    });
    
    const espGuardado = localStorage.getItem('especialista_id');
    if (espGuardado) especialistaSelect.value = espGuardado;
    
    cargarCitas();

// Cambiar estado de la cita
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
        
        if (!csrfToken) {
            console.error("¡Error fatal! No se pudo encontrar el CSRF token en las cookies.");
        }
        return csrfToken;
    }
   
    tablaCitasBody.addEventListener('click', function(event) {
        
        const botonEstado = event.target.closest('.btn-cambiar-estado');
        
        if (botonEstado) {
            event.preventDefault(); 

            const citaId = botonEstado.dataset.idCita;
            const nuevoEstado = botonEstado.dataset.estado;
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
                    'cita_id': citaId,
                    'nuevo_estado': nuevoEstado
                })
            })
            .then(response => {
                if (!response.ok) throw new Error('Falló la petición a la API de estado');
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    const fila = botonEstado.closest('tr');
                    const badge = fila.querySelector('.badge');
                    
                    if (badge) {
                        badge.textContent = data.nuevo_estado;
                        badge.className = 'badge'; 
                        if (data.nuevo_estado === 'Confirmada') {
                            badge.classList.add('text-bg-success');
                        } else if (data.nuevo_estado === 'Cancelada') {
                            badge.classList.add('text-bg-danger');
                        } else {
                            badge.classList.add('text-bg-secondary');
                        }
                    }
                } else {
                    alert('Error al actualizar la cita: ' + (data.error || 'Desconocido'));
                }
            })
            .catch(error => {
                console.error('Error en fetch (cambiar estado):', error);
                alert('Error de conexión al intentar cambiar el estado.');
            });
            
            return; 
        } 

        const botonWhatsapp = event.target.closest('.btn-accion-whatsapp.disabled');
        
        if (botonWhatsapp) {
            event.preventDefault(); 
            console.log("Clic detenido: Teléfono no registrado.");
            return; 
        }
        
    });

// Manejo del modal "Crear Cita"
    let filtroEspecialista = document.getElementById('filtro-especialista').value;
    if (!filtroEspecialista) {
        filtroEspecialista = localStorage.getItem('especialista_id') || '';
    }
    
    const modalCrearCita = document.getElementById('modalCrearCita');
    const modalBody = document.getElementById('modal-body-form-cita');
    
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
                    if (typeof configurarFormularioCita === 'function') configurarFormularioCita();
                })
                .catch(error => {
                    console.error('Error:', error);
                    modalBody.innerHTML = `<div class="alert alert-danger">Error al cargar. Por favor, intenta de nuevo.</div>`;
                });
        });
    }

    // manejo del modal para editar cita
    const modalEditarCita = document.getElementById('modalEditarCita');
    if (modalEditarCita) {
        modalEditarCita.addEventListener('show.bs.modal', function (event) {
            
            const boton = event.relatedTarget;
            const citaId = boton.dataset.idCita;
            
            const url = urlEditarCitaTemplate.replace('/0/', `/${citaId}/`);
            
            const modalBody = document.getElementById('modal-body-form-editar-cita');
            
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

}); 

// Configuración del formulario de cita
function configurarFormularioCita() {
    
    const form = document.getElementById('form-crear-cita');
    const modalCrearCita = document.getElementById('modalCrearCita'); 
    const modalEditarCita = document.getElementById('modalEditarCita');
    const input = document.getElementById('buscarPaciente');
    
    if (!form) {
        console.warn("configurarFormularioCita: No se encontró el formulario 'form-crear-cita'.");
        return; 
    }

    if (input) {
        const resultados = document.getElementById('resultadosPacientes');
        const hiddenInput = document.getElementById('paciente_id');

        input.addEventListener('keyup', function() {
            if (input.disabled) { 
                resultados.innerHTML = '';
                return;
            }
            
            fetch(`${buscarPacientesURL}?q=${encodeURIComponent(input.value.trim())}`)
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
                        item.innerHTML = `<strong>${p.nombre} ${p.apellido}</strong> <small class="text-muted">(${p.telefono || 'Sin teléfono'})</small>`;
                        item.addEventListener('click', (e) => {
                            e.preventDefault();
                            input.value = `${p.nombre} ${p.apellido}`;
                            hiddenInput.value = p.id;
                            resultados.innerHTML = '';
                        });
                        resultados.appendChild(item);
                    });
                })
                .catch(error => console.error('Error en fetch buscar_pacientes:', error));
        });
    } 

    const checkNuevo = document.getElementById('check-nuevo-paciente');
    if (checkNuevo) {
        const contNuevo = document.getElementById('campos-nuevo-paciente');
        const inputNombre = document.getElementById('nuevo_paciente_nombre');
        const inputApellido = document.getElementById('nuevo_paciente_apellido');
        const hiddenInput = document.getElementById('paciente_id'); 

        checkNuevo.addEventListener('change', function() {
            if (this.checked) {
                input.disabled = true;
                input.classList.add('bg-light');
                input.value = '';
                if (document.getElementById('resultadosPacientes')) document.getElementById('resultadosPacientes').innerHTML = ''; 
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
    } 

    const duiInput = document.getElementById('id_dui');
    if (duiInput && typeof IMask !== 'undefined') {
        IMask(duiInput, { mask: '00000000-0' });
    } else if (typeof IMask === 'undefined') {
        console.error("IMask.js no se cargó.");
    }

    
    form.addEventListener('submit', function(event) {
        event.preventDefault(); 
        
        const submitButton = form.closest('.modal-content').querySelector('.modal-footer button[type="submit"]');
        
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Guardando...';
        }

        const formData = new FormData(form);

        fetch(form.action, { 
            method: 'POST',
            body: formData,
            headers: { 'X-CSRFToken': formData.get('csrfmiddlewaretoken') }
        })
        .then(response => response.json().then(data => ({ ok: response.ok, status: response.status, data })))
        .then(({ ok, status, data }) => {
            if (ok) {
                const modalActivo = bootstrap.Modal.getInstance(form.closest('.modal'));
                if (modalActivo) {
                    modalActivo.hide();
                }
                
                try {
                    cargarCitas(); 
                } catch (e) {
                    window.location.reload();
                }

            } else if (status === 400) {
                alert(`Error: ${data.error}`); 
                if (submitButton) {
                    submitButton.disabled = false;
                    submitButton.innerHTML = 'Guardar Cita';
                }
            } else {
                throw new Error(data.error || 'Error del servidor.');
            }
        })
        .catch(error => {
            console.error('Error al enviar el formulario:', error);
            alert('Ocurrió un error inesperado.');
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.innerHTML = 'Guardar Cita';
            }
        });
    });

    const selectTratamiento = document.getElementById('tratamiento');
    const duracionSpan = document.getElementById('duracion-minutos');

    if (selectTratamiento && duracionSpan) { 
        selectTratamiento.addEventListener('change', function () {
            
            if (!this.selectedOptions || this.selectedOptions.length === 0) {
                duracionSpan.textContent = '—';
                return;
            }
            const duracion = parseInt(this.selectedOptions[0].dataset.duracion);

            if (isNaN(duracion) || duracion <= 0) {
                duracionSpan.textContent = '—';
                return;
            }

            const horas = Math.floor(duracion / 60);
            const minutos = duracion % 60;

            let texto = '';
            if (horas > 0) texto += horas === 1 ? '1 hora' : `${horas} horas`;
            if (minutos > 0) {
                texto += horas > 0 ? ' y ' : '';
                texto += `${minutos} minutos`;
            }
            duracionSpan.textContent = texto;
        });

        selectTratamiento.dispatchEvent(new Event('change'));
    }
    
}