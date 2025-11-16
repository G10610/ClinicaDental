from django.shortcuts import render, get_object_or_404
from datetime import date, time, datetime, timedelta
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from gestionespecialistas.models import Especialista
from gestiontratamientos.models import Tratamiento
from gestiondepacientes.forms import PacienteRapidoForm
from gestiondepacientes.models import Paciente
from .models import Cita
from django.db.models import Q, Value
from datetime import timezone as dt_timezone
from django.utils import timezone
from configuracion.models import ConfiguracionClinica
from django.utils import formats
from django.db.models.functions import Concat
import json
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt


@login_required
def agenda(request):
    today = date.today().strftime('%Y-%m-%d')
    especialista_id_str = request.GET.get('especialista_id')

    especialista_seleccionado_id = None
    if especialista_id_str:
        try:
            especialista_seleccionado_id = int(especialista_id_str)
        except ValueError:
            pass 

    lista_especialistas = Especialista.objects.all()

    context = {
        'today': today,
        'lista_especialistas': lista_especialistas,
        'especialista_seleccionado_id': especialista_seleccionado_id,
        'active_page': 'agenda',
    }
    return render(request, 'agenda.html', context)


@login_required
def crear_cita(request):
    especialistas = Especialista.objects.all()
    tratamientos = Tratamiento.objects.all()

    if request.method == "POST":
        registrar_nuevo = request.POST.get('check-nuevo-paciente') == 'on'

        #Determinar el paciente
        if registrar_nuevo:
            form_data = {
                'nombre': request.POST.get('nombre'),
                'apellido': request.POST.get('apellido'),
                'telefono': request.POST.get('telefono'),
                'dui': request.POST.get('dui'),
            }
            paciente_form = PacienteRapidoForm(form_data)

            if paciente_form.is_valid():
                nuevo_paciente = paciente_form.save(commit=False)
                nuevo_paciente.fecha_ingreso = timezone.now().date()
                nuevo_paciente.save()
            else:
                return JsonResponse({'error': paciente_form.errors}, status=400)
        else:
            paciente_id = request.POST.get('paciente_id')
            if not paciente_id:
                return JsonResponse({'error': 'Debe seleccionar un paciente existente.'}, status=400)
            try:
                nuevo_paciente = Paciente.objects.get(id=paciente_id)
            except Paciente.DoesNotExist:
                return JsonResponse({'error': 'Paciente no encontrado.'}, status=400)

        # Validar fecha y hora
        fecha_str = request.POST.get('fecha')
        hora_str = request.POST.get('hora')

        if not fecha_str or not hora_str:
            return JsonResponse({'error': 'Debe seleccionar fecha y hora.'}, status=400)

        try:
            naive_dt = datetime.strptime(f"{fecha_str} {hora_str}", '%Y-%m-%d %H:%M')
            aware_dt = timezone.make_aware(naive_dt, timezone.get_current_timezone())
            aware_dt = aware_dt.astimezone(dt_timezone.utc)

        except Exception as e:
            return JsonResponse({'error': f'Error en la fecha/hora: {e}'}, status=400)

        #Validar solapamientos
        especialista_id = request.POST.get('especialista_id')
        tratamiento_id = request.POST.get('tratamiento_id')

        if not tratamiento_id:
            return JsonResponse({'error': 'Debe seleccionar un tratamiento.'}, status=400)

        try:
            tratamiento = Tratamiento.objects.get(id=tratamiento_id)
        except Tratamiento.DoesNotExist:
            return JsonResponse({'error': 'Tratamiento inválido.'}, status=400)

        duracion = getattr(tratamiento, 'duracion_minutos', None)
        try:
            duracion = int(duracion) if duracion is not None else 30
        except (ValueError, TypeError):
            duracion = 30

        inicio_nueva = aware_dt
        fin_nueva = aware_dt + timedelta(minutes=duracion)

        citas_existentes = Cita.objects.filter(especialista_id=especialista_id)

        for cita in citas_existentes:
            dur_cita = 30
            if cita.tratamiento and getattr(cita.tratamiento, 'duracion_minutos', None):
                try:
                    dur_cita = int(cita.tratamiento.duracion_minutos)
                except (ValueError, TypeError):
                    dur_cita = 30

            inicio_cita = cita.fecha_hora
            fin_cita = inicio_cita + timedelta(minutes=dur_cita)

            if inicio_nueva < fin_cita and inicio_cita < fin_nueva:
                return JsonResponse({
                    'error': 'Existe una cita que se superpone con ese horario.'
                }, status=400)


        # Crear la cita
        Cita.objects.create(
            paciente=nuevo_paciente,
            especialista_id=especialista_id,
            tratamiento_id=request.POST.get('tratamiento_id'),
            fecha_hora=aware_dt,
            detalles=request.POST.get('detalles', ''),
            estado='Confirmada'
        )

        return JsonResponse({'success': True})

    # Método GET: Construir formulario
    else:
        config = ConfiguracionClinica.objects.first()
        if not config:
            ConfiguracionClinica.objects.create()
            config = ConfiguracionClinica.objects.first()

        fecha_str = request.GET.get('fecha')
        hora_str = request.GET.get('hora')
        especialista_id = request.GET.get('especialista_id')

        slots_disponibles = []
        view_mode = 'weekly'

        if not hora_str:
            # Vista de agenda diaria
            view_mode = 'daily'
            
            hora_str = config.hora_apertura.strftime('%H:%M')
            
            # Generar lista de slots cada 15 MINUTOS
            try:
                hora_actual = datetime.combine(date.today(), config.hora_apertura)
                hora_fin = datetime.combine(date.today(), config.hora_cierre)
                intervalo = timedelta(minutes=15) 

                while hora_actual < hora_fin:
                    slots_disponibles.append(hora_actual.time())
                    hora_actual += intervalo
            except Exception as e:
                print("Error generando slots para agenda diaria:", e)


        fecha_legible = "" 
        if fecha_str:
            try:
                fecha_obj = datetime.fromisoformat(fecha_str).date()
                
                # El \d\e es para escapar "de"
                fecha_legible = formats.date_format(fecha_obj, "l j \d\e F \d\e Y")
                
                fecha_legible = fecha_legible.capitalize()
            except (ValueError, TypeError):
                fecha_legible = "Fecha inválida"

            slots_disponibles = []
            local_tz = timezone.get_current_timezone()
            if especialista_id and fecha_str:
                try:
                    intervalo_min = 15
                    intervalo_td = timedelta(minutes=intervalo_min)

                    # 1. Generar todos los slots posibles del día
                    slots_posibles = []
                    hora_actual = datetime.combine(
                        datetime.today(), config.hora_apertura)
                    hora_fin = datetime.combine(
                        datetime.today(), config.hora_cierre)

                    while hora_actual < hora_fin:
                        slots_posibles.append(hora_actual.time())
                        hora_actual += intervalo_td

                    # 2. Obtener citas existentes
                    fecha_local = datetime.fromisoformat(fecha_str).date()
                    dia_inicio = timezone.make_aware(
                        datetime.combine(fecha_local, time.min), local_tz)
                    dia_fin = timezone.make_aware(
                        datetime.combine(fecha_local, time.max), local_tz)

                    citas_ese_dia = Cita.objects.filter(
                        especialista_id=especialista_id,
                        fecha_hora__range=(dia_inicio, dia_fin)
                    ).select_related('tratamiento') # Importante incluir tratamiento

                    # 3. Crear un set con TODOS los slots ocupados
                    citas_ocupadas_set = set()
                    for cita in citas_ese_dia:
                        hora_inicio_cita = cita.fecha_hora.astimezone(
                            local_tz).time()

                        duracion_real = 30 
                        if cita.tratamiento and cita.tratamiento.duracion_minutos:
                            duracion_real = cita.tratamiento.duracion_minutos

                        # Redondea hacia arriba
                        num_slots = int(duracion_real // intervalo_min)
                        if duracion_real % intervalo_min > 0:
                            num_slots += 1

                        temp_dt = datetime.combine(date.today(), hora_inicio_cita)
                        for i in range(num_slots):
                            citas_ocupadas_set.add(temp_dt.time())
                            temp_dt += intervalo_td

                    # 4. Filtrar la lista
                    for slot in slots_posibles:
                        if slot not in citas_ocupadas_set:
                            slots_disponibles.append(slot)

                except (ValueError, TypeError) as e:
                    print("Error generando slots:", e)
                    slots_disponibles = []

        initial_data = {
            'especialista_id': especialista_id,
            'fecha': fecha_str,
            'hora': hora_str,
            'fecha_legible': fecha_legible
        }

        context = {
            'especialistas': especialistas,
            'tratamientos': tratamientos,
            'initial_data': initial_data,
            'slots_disponibles': slots_disponibles,
            'view_mode': view_mode
        }
        return render(request, 'form_cita.html', context)


def buscar_pacientes(request):
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse([], safe=False)

    q = " ".join(q.split()) 

    pacientes = (
        Paciente.objects.annotate(
            nombre_completo=Concat('nombre', Value(' '), 'apellido')
        )
        .filter(
            Q(nombre__icontains=q) |
            Q(apellido__icontains=q) |
            Q(nombre_completo__icontains=q)
        )
        .only('id', 'nombre', 'apellido', 'telefono') 
        .order_by('nombre')[:10]
    )

    data = [
        {'id': p.id, 'nombre': p.nombre, 'apellido': p.apellido, 'telefono': p.telefono}
        for p in pacientes
    ]
    return JsonResponse(data, safe=False)

@login_required
def api_get_citas(request):
    fecha_str = request.GET.get('fecha')
    especialista_id = request.GET.get('especialista_id')

    if not especialista_id or not fecha_str:
        return JsonResponse({'error': 'Faltan parámetros'}, status=400)

    # Usar la misma lógica de filtro de zona horaria
    lista_citas_obj = []
    local_tz = timezone.get_current_timezone()
    try:
        fecha_local = datetime.fromisoformat(fecha_str).date()
        dia_inicio = timezone.make_aware(datetime.combine(fecha_local, datetime.min.time()), local_tz)
        dia_fin = timezone.make_aware(datetime.combine(fecha_local, datetime.max.time()), local_tz)

        lista_citas_obj = Cita.objects.filter(
            especialista_id=especialista_id, 
            fecha_hora__range=(dia_inicio, dia_fin)
        ).select_related(
            'paciente', 'tratamiento' # Optimización
        ).order_by(
            'fecha_hora'
        )

    except (ValueError, TypeError) as e:
        print("Error en api_get_citas:", e)
        return JsonResponse({'citas': []})

    citas_json = []
    for cita in lista_citas_obj:
        # Convertir UTC a hora local
        hora_local = cita.fecha_hora.astimezone(local_tz)
        
        citas_json.append({
            'id': cita.id,
            'hora': hora_local.strftime('%I:%M %p'),
            'paciente_nombre': f"{cita.paciente.nombre} {cita.paciente.apellido}",
            'tratamiento_nombre': cita.tratamiento.nombre if cita.tratamiento else 'N/A',
            'paciente_id': cita.paciente.id,
            'paciente_telefono': cita.paciente.telefono or '',
            'estado': cita.estado or 'Pendiente',
        })

    return JsonResponse({'citas': citas_json})


def agenda_semanal(request):
    fecha_str = request.GET.get('fecha')
    today = date.fromisoformat(fecha_str) if fecha_str else date.today()

    start_of_week = today - timedelta(days=today.weekday())

    config = ConfiguracionClinica.objects.first() 
    if not config:
        hora_inicio = time(8, 0)
        hora_fin = time(18, 0)
        intervalo = 30
        dias_laborales = [0, 1, 2, 3, 4, 5]
    else:
        hora_inicio = config.hora_apertura
        hora_fin = config.hora_cierre
        intervalo = config.intervalo_citas
        dias_laborales = config.get_dias_laborales_lista()

    dias_semana = [start_of_week + timedelta(days=d) for d in dias_laborales]

    def generar_horas(hora_inicio, hora_fin, intervalo):
        horas = []
        actual = datetime.combine(date.today(), hora_inicio)
        fin = datetime.combine(date.today(), hora_fin)
        while actual <= fin:
            horas.append(actual.strftime("%H:%M"))
            actual += timedelta(minutes=intervalo)
        return horas

    horas = generar_horas(hora_inicio, hora_fin, intervalo)

    especialista_id_str = request.GET.get('especialista_id')
    especialista_seleccionado_id = None
    if especialista_id_str:
        try:
            especialista_seleccionado_id = int(especialista_id_str)
        except ValueError:
            pass

    lista_especialistas = Especialista.objects.all()

    context = {
            'lista_especialistas': lista_especialistas,
            'today': today,
            'especialista_seleccionado_id': especialista_seleccionado_id,
            'view_name': 'agenda_semanal',
            'dias_semana': dias_semana,
            'horas_dia': horas,
            'active_page': 'agenda',
            'intervalo': intervalo
        }


    return render(request, 'agenda_semanal.html', context)



@login_required
def api_get_citas_semana(request):
    fecha_inicio_str = request.GET.get('fecha_inicio') 
    especialista_id = request.GET.get('especialista_id')

    if not especialista_id or not fecha_inicio_str:
        return JsonResponse({'error': 'Faltan parámetros'}, status=400)

    lista_citas_obj = []
    local_tz = timezone.get_current_timezone()
    try:
        lunes_local = datetime.fromisoformat(fecha_inicio_str).date()
        domingo_local = lunes_local + timedelta(days=6)

        semana_inicio = timezone.make_aware(datetime.combine(lunes_local, datetime.min.time()), local_tz)
        semana_fin = timezone.make_aware(datetime.combine(domingo_local, datetime.max.time()), local_tz)
        
        lista_citas_obj = Cita.objects.filter(
            especialista_id=especialista_id, 
            fecha_hora__range=(semana_inicio, semana_fin) 
        ).select_related(
            'paciente', 'tratamiento'
        ).order_by(
            'fecha_hora'
        )

    except (ValueError, TypeError) as e:
        print("Error en api_get_citas_semana:", e)
        return JsonResponse({'citas': []})

    # Filtro de días laborales
    config = ConfiguracionClinica.objects.first()
    if config:
        dias_laborales_indices = config.get_dias_laborales_lista() # ej: [0, 1, 3, 5]
    else:
        dias_laborales_indices = [0, 1, 2, 3, 4, 5] # Default L-S

    print(f"DEBUG (API): Filtrando citas para días: {dias_laborales_indices}")
    
    citas_filtradas = []
    for cita in lista_citas_obj:
        hora_local = cita.fecha_hora.astimezone(local_tz)
        
        # Comprueba si el día de la cita está en la lista permitida
        if hora_local.weekday() in dias_laborales_indices:
            citas_filtradas.append(cita)

    citas_json = []
    for cita in citas_filtradas: 
        hora_local = cita.fecha_hora.astimezone(local_tz)
        
        duracion_minutos = 30
        if cita.tratamiento and cita.tratamiento.duracion_minutos:
            duracion_minutos = cita.tratamiento.duracion_minutos
        
        citas_json.append({
            'id': cita.id,
            'fecha': hora_local.strftime('%Y-%m-%d'),
            'hora': hora_local.strftime('%H:%M'),
            'paciente_id': cita.paciente.id, 
            'paciente_telefono': cita.paciente.telefono if cita.paciente else "",
            'paciente_nombre': f"{cita.paciente.nombre} {cita.paciente.apellido}",
            'tratamiento_nombre': cita.tratamiento.nombre if cita.tratamiento else 'N/A',
            'estado': cita.estado or 'Pendiente',
            'duracion': duracion_minutos
        })

    return JsonResponse({'citas': citas_json})


    

@login_required
@require_POST
def api_cambiar_estado(request):
    try:
        data = json.loads(request.body)
        cita_id = data.get('cita_id')
        nuevo_estado = data.get('nuevo_estado')

        estados_validos = ['Pendiente', 'Confirmada', 'Cancelada']
        if nuevo_estado not in estados_validos:
            return JsonResponse({'error': 'Estado no válido'}, status=400)

        try:
            cita = Cita.objects.get(id=cita_id)
            cita.estado = nuevo_estado
            cita.save(update_fields=['estado']) 

            return JsonResponse({'success': True, 'nuevo_estado': nuevo_estado})

        except Cita.DoesNotExist:
            return JsonResponse({'error': 'Cita no encontrada'}, status=404)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def editar_cita(request, cita_id):
    
    cita = get_object_or_404(Cita, id=cita_id)
    
    if request.method == "POST":
        # Lógica POST
        try:
            tratamiento_id = request.POST.get('tratamiento_id')
            detalles = request.POST.get('detalles', '')
            fecha_str = request.POST.get('fecha')
            hora_str = request.POST.get('hora')
            local_tz = timezone.get_current_timezone()

            if not tratamiento_id:
                return JsonResponse({'error': 'Debe seleccionar un tratamiento.'}, status=400)
            
            tratamiento = Tratamiento.objects.get(id=tratamiento_id)
            duracion = getattr(tratamiento, 'duracion_minutos', 30)
            
            naive_dt = datetime.strptime(f"{fecha_str} {hora_str}", '%Y-%m-%d %H:%M')
            inicio_nueva = timezone.make_aware(naive_dt, local_tz)
            fin_nueva = inicio_nueva + timedelta(minutes=duracion)

            citas_existentes = Cita.objects.filter(
                especialista_id=cita.especialista_id
            ).exclude(id=cita.id) # Excluye la cita actual

            for c in citas_existentes.select_related('tratamiento'):
                dur_cita = 30
                if c.tratamiento and getattr(c.tratamiento, 'duracion_minutos', None):
                    dur_cita = int(c.tratamiento.duracion_minutos)
                
                inicio_cita = c.fecha_hora.astimezone(local_tz) 
                fin_cita = inicio_cita + timedelta(minutes=dur_cita)

                if inicio_nueva < fin_cita and inicio_cita < fin_nueva:
                    return JsonResponse({
                        'error': 'El nuevo horario se superpone con otra cita existente.'
                    }, status=400)
            
            cita.tratamiento_id = tratamiento_id
            cita.detalles = detalles
            cita.fecha_hora = inicio_nueva.astimezone(dt_timezone.utc)
            cita.save()
            
            return JsonResponse({'success': True})

        except Tratamiento.DoesNotExist:
            return JsonResponse({'error': 'Tratamiento inválido.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Error al guardar: {str(e)}'}, status=400)

    else:
        # Lógica GET
        
        especialistas = Especialista.objects.all()
        tratamientos = Tratamiento.objects.all()
        config = ConfiguracionClinica.objects.first() or ConfiguracionClinica.objects.create()
        
        local_tz = timezone.get_current_timezone()
        hora_local = cita.fecha_hora.astimezone(local_tz)
        
        fecha_obj = hora_local.date()
        fecha_str = fecha_obj.strftime('%Y-%m-%d')
        fecha_legible = formats.date_format(fecha_obj, "l j \d\e F \d\e Y").capitalize()

        slots_disponibles = []
        if cita.especialista_id and fecha_str:
            try:
                intervalo_min = 15 # Forzamos 15 minutos
                intervalo_td = timedelta(minutes=intervalo_min)

                # 1. Generar todos los slots posibles (cada 15 min)
                slots_posibles = []
                hora_actual_dt = datetime.combine(datetime.today(), config.hora_apertura)
                hora_fin_dt = datetime.combine(datetime.today(), config.hora_cierre)
                
                while hora_actual_dt < hora_fin_dt:
                    slots_posibles.append(hora_actual_dt.time())
                    hora_actual_dt += intervalo_td

                # 2. Obtener citas existentes (excluyendo la actual)
                dia_inicio = timezone.make_aware(datetime.combine(fecha_obj, time.min), local_tz)
                dia_fin = timezone.make_aware(datetime.combine(fecha_obj, time.max), local_tz)

                citas_ese_dia = Cita.objects.filter(
                    especialista_id=cita.especialista_id, 
                    fecha_hora__range=(dia_inicio, dia_fin)
                ).exclude(id=cita_id).select_related('tratamiento')

                # 3. Crear set de slots ocupados
                citas_ocupadas_set = set()
                for c in citas_ese_dia:
                    hora_inicio_cita = c.fecha_hora.astimezone(local_tz).time()
                    
                    duracion = 30 
                    if c.tratamiento and c.tratamiento.duracion_minutos:
                        duracion = c.tratamiento.duracion_minutos
                    
                    num_slots = int(duracion // intervalo_min)
                    if duracion % intervalo_min > 0:
                        num_slots += 1
                    
                    temp_dt = datetime.combine(date.today(), hora_inicio_cita)
                    for i in range(num_slots):
                        citas_ocupadas_set.add(temp_dt.time())
                        temp_dt += intervalo_td

                # 4. Filtrar la lista
                for slot in slots_posibles:
                    if slot not in citas_ocupadas_set: 
                        slots_disponibles.append(slot)
                
            except (ValueError, TypeError) as e:
                print(f"Error generando slots para editar: {e}")
                slots_disponibles = []

        initial_data = {
            'especialista_id': str(cita.especialista.id),
            'fecha': fecha_str,
            'hora': hora_local.strftime('%H:%M'), # Hora pre-seleccionada
            'fecha_legible': fecha_legible
        }
        
        context = {
            'especialistas': especialistas,
            'tratamientos': tratamientos,
            'initial_data': initial_data,
            'slots_disponibles': slots_disponibles,
            'cita_instancia': cita,
            'view_mode': 'daily' # Para que el HTML muestre el <select>
        }
        
        return render(request, 'form_cita.html', context)