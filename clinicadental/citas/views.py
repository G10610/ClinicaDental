from django.shortcuts import render
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


@login_required
def agenda(request):
    today = date.today().strftime('%Y-%m-%d')
    especialista_id_str = request.GET.get('especialista_id')

    especialista_seleccionado_id = None
    if especialista_id_str:
        try:
            especialista_seleccionado_id = int(especialista_id_str)
        except ValueError:
            pass  # Ignora si no es número

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

        # 🔹 Paso 1: determinar el paciente
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

        # 🔹 Paso 2: validar fecha y hora
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

        # 🔹 Paso 3: verificar si ya hay una cita a esa hora con ese especialista
        especialista_id = request.POST.get('especialista_id')
        cita_existente = Cita.objects.filter(
            especialista_id=especialista_id,
            fecha_hora=aware_dt
        ).exists()

        if cita_existente:
            return JsonResponse({'error': 'Esa hora ya está ocupada para el especialista seleccionado.'}, status=400)

        # 🔹 Paso 4: crear la cita
        Cita.objects.create(
            paciente=nuevo_paciente,
            especialista_id=especialista_id,
            tratamiento_id=request.POST.get('tratamiento_id'),
            fecha_hora=aware_dt,
            detalles=request.POST.get('detalles', '')
        )

        return JsonResponse({'success': True})

    # 🔹 Método GET → construir formulario y horas disponibles
    else:
        config = ConfiguracionClinica.objects.first()
        if not config:
            config = ConfiguracionClinica.objects.create()

        fecha_str = request.GET.get('fecha')
        especialista_id = request.GET.get('especialista_id')

        fecha_legible = "" # Valor por defecto
        if fecha_str:
            try:
                # 1. Convertimos el string "2025-11-05" a un objeto fecha
                fecha_obj = datetime.fromisoformat(fecha_str).date()
                
                # 2. Usamos Django para formatearlo en español
                # "l" = día (Miércoles), "j" = 5, "F" = noviembre, "Y" = 2025
                # El \d\e es para escapar "de" y que no se interprete como formato
                fecha_legible = formats.date_format(fecha_obj, "l j \d\e F \d\e Y")
                
                # 3. Capitalizamos (suele salir "miércoles", lo queremos "Miércoles")
                fecha_legible = fecha_legible.capitalize()
            except (ValueError, TypeError):
                fecha_legible = "Fecha inválida" # Por si algo falla

        slots_disponibles = []
        local_tz = timezone.get_current_timezone()

        if especialista_id and fecha_str:
            try:
                # 1️⃣ Generar todas las horas posibles
                slots_posibles = []
                hora_actual = datetime.combine(datetime.today(), config.hora_apertura)
                hora_fin = datetime.combine(datetime.today(), config.hora_cierre)
                intervalo = timedelta(minutes=config.intervalo_citas)

                while hora_actual < hora_fin:
                    slots_posibles.append(hora_actual.time())
                    hora_actual += intervalo

                # 2️⃣ Crear un RANGO de 24h en tu zona horaria local
                fecha_local = datetime.fromisoformat(fecha_str).date()
                
                # Creamos datetimes "ingenuos" (naive)
                naive_dia_inicio = datetime.combine(fecha_local, datetime.min.time())
                naive_dia_fin = datetime.combine(fecha_local, datetime.max.time())

                # Usamos 'make_aware' (la forma correcta) en lugar de 'localize'
                dia_inicio = timezone.make_aware(naive_dia_inicio, local_tz)
                dia_fin = timezone.make_aware(naive_dia_fin, local_tz)
                

                # 2️⃣ Obtener citas existentes (UTC → convertir a local)
                citas_ese_dia = Cita.objects.filter(
                    especialista_id=especialista_id, 
                    fecha_hora__range=(dia_inicio, dia_fin) # <-- ¡FILTRO CORREGIDO!
                )

                citas_ocupadas_set = set()
                for cita in citas_ese_dia:
                    hora_local = cita.fecha_hora.astimezone(local_tz).time() # ej. time(8, 0)
                    citas_ocupadas_set.add(hora_local)

                for cita in citas_ese_dia:
                    hora_local = cita.fecha_hora.astimezone(local_tz)
                    hora_normalizada = hora_local.replace(second=0, microsecond=0).time()
                    citas_ocupadas_set.add(hora_normalizada)

                # 6. Filtrar la lista: quitar las horas ocupadas
                for slot in slots_posibles:
                    if slot not in citas_ocupadas_set: 
                        slots_disponibles.append(slot)

            except (ValueError, TypeError) as e:
                print("Error generando slots:", e)
                slots_disponibles = []

        initial_data = {
            'especialista_id': especialista_id,
            'fecha': fecha_str,
            'fecha_legible': fecha_legible
        }

        context = {
            'especialistas': especialistas,
            'tratamientos': tratamientos,
            'initial_data': initial_data,
            'slots_disponibles': slots_disponibles,
        }
        return render(request, 'form_cita.html', context)


def buscar_pacientes(request):
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse([], safe=False)

    # Normalizamos el término de búsqueda
    q = " ".join(q.split())  # elimina espacios extra

    # Anotamos el campo "nombre_completo" para comparar nombre + apellido juntos
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
    """
    Esta vista devuelve las citas de un día y especialista
    específicos en formato JSON.
    """
    # 1. Obtener los parámetros del 'fetch' de JavaScript
    fecha_str = request.GET.get('fecha')
    especialista_id = request.GET.get('especialista_id')

    # 2. Validar que tenemos los datos necesarios
    if not especialista_id or not fecha_str:
        return JsonResponse({'error': 'Faltan parámetros'}, status=400)

    # 3. Usamos la MISMA lógica de filtro de zona horaria que en 'crear_cita'
    #    (Esto es crucial para que coincidan)
    lista_citas_obj = []
    local_tz = timezone.get_current_timezone()
    try:
        fecha_local = datetime.fromisoformat(fecha_str).date()
        dia_inicio = timezone.make_aware(datetime.combine(fecha_local, datetime.min.time()), local_tz)
        dia_fin = timezone.make_aware(datetime.combine(fecha_local, datetime.max.time()), local_tz)

        # 4. Consultar la base de datos
        lista_citas_obj = Cita.objects.filter(
            especialista_id=especialista_id, 
            fecha_hora__range=(dia_inicio, dia_fin)
        ).select_related(
            'paciente', 'tratamiento' # Optimización para no golpear la BD
        ).order_by(
            'fecha_hora' # ¡Como pediste!
        )

    except (ValueError, TypeError) as e:
        print("Error en api_get_citas:", e)
        # Devolvemos una lista vacía si hay un error
        return JsonResponse({'citas': []})

    # 5. Convertir los objetos de Django en un JSON simple
    citas_json = []
    for cita in lista_citas_obj:
        # Convertimos la hora UTC de la BD a la hora local para mostrarla
        hora_local = cita.fecha_hora.astimezone(local_tz)
        
        citas_json.append({
            'id': cita.id,
            'hora': hora_local.strftime('%I:%M %p'), # Formato: "09:30 AM"
            'paciente_nombre': f"{cita.paciente.nombre} {cita.paciente.apellido}",
            'tratamiento_nombre': cita.tratamiento.nombre if cita.tratamiento else 'N/A',
            'estado': cita.estado or 'Pendiente', # Usar 'Pendiente' si está vacío
        })

    return JsonResponse({'citas': citas_json})


def agenda_semanal(request):
    # Fecha base (hoy o la seleccionada)
    fecha_str = request.GET.get('fecha')
    today = date.fromisoformat(fecha_str) if fecha_str else date.today()

    # Semana: de lunes a domingo (o según configuración más adelante)
    start_of_week = today - timedelta(days=today.weekday())

    config = ConfiguracionClinica.objects.first()  # usamos la configuración global
    if not config:
        # Valores por defecto si no hay configuración
        hora_inicio = time(8, 0)
        hora_fin = time(18, 0)
        intervalo = 30
        dias_laborales = [0, 1, 2, 3, 4, 5]
    else:
        hora_inicio = config.hora_apertura
        hora_fin = config.hora_cierre
        intervalo = config.intervalo_citas
        dias_laborales = config.get_dias_laborales_lista()
        print(f"DEBUG (View): Dibujando tabla para días: {dias_laborales}")

    # --- Días según configuración ---
    dias_semana = [start_of_week + timedelta(days=d) for d in dias_laborales]

    # --- Generar intervalos de hora ---
    def generar_horas(hora_inicio, hora_fin, intervalo):
        horas = []
        actual = datetime.combine(date.today(), hora_inicio)
        fin = datetime.combine(date.today(), hora_fin)
        while actual <= fin:
            horas.append(actual.strftime("%H:%M"))
            actual += timedelta(minutes=intervalo)
        return horas

    horas = generar_horas(hora_inicio, hora_fin, intervalo)

    # Obtener id del especialista seleccionado
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
        
    }

    return render(request, 'agenda_semanal.html', context)



@login_required
def api_get_citas_semana(request):
    """
    Esta vista devuelve las citas de una SEMANA completa y un especialista
    específicos en formato JSON.
    """
    # 1. Obtener los parámetros
    #    Cambiamos 'fecha' por 'fecha_inicio' para más claridad
    fecha_inicio_str = request.GET.get('fecha_inicio') 
    especialista_id = request.GET.get('especialista_id')

    # 2. Validar que tenemos los datos necesarios
    if not especialista_id or not fecha_inicio_str:
        return JsonResponse({'error': 'Faltan parámetros'}, status=400)

    lista_citas_obj = []
    local_tz = timezone.get_current_timezone()
    try:
        # 3. Lógica de Rango de Fechas (¡Aquí está el cambio principal!)
        
        # Convertimos la fecha de inicio (que debería ser un lunes)
        lunes_local = datetime.fromisoformat(fecha_inicio_str).date()
        
        # Calculamos el último día de esa semana (domingo)
        domingo_local = lunes_local + timedelta(days=6)

        # Creamos el rango consciente de la zona horaria, igual que antes
        semana_inicio = timezone.make_aware(datetime.combine(lunes_local, datetime.min.time()), local_tz)
        semana_fin = timezone.make_aware(datetime.combine(domingo_local, datetime.max.time()), local_tz)
        
        # 4. Consultar la base de datos
        lista_citas_obj = Cita.objects.filter(
            especialista_id=especialista_id, 
            # Usamos el nuevo rango de 7 días
            fecha_hora__range=(semana_inicio, semana_fin) 
        ).select_related(
            'paciente', 'tratamiento'
        ).order_by(
            'fecha_hora'
        )

    except (ValueError, TypeError) as e:
        print("Error en api_get_citas_semana:", e)
        return JsonResponse({'citas': []})


    # --- ¡ESTE ES EL FILTRO CRÍTICO! ---
    # Asegúrate de que este bloque exista
    config = ConfiguracionClinica.objects.first()
    if config:
        dias_laborales_indices = config.get_dias_laborales_lista() # ej: [0, 1, 3, 5]
    else:
        dias_laborales_indices = [0, 1, 2, 3, 4, 5] # Default L-S

    print(f"DEBUG (API): Filtrando citas para días: {dias_laborales_indices}")
    
    citas_filtradas = []
    for cita in lista_citas_obj:
        hora_local = cita.fecha_hora.astimezone(local_tz)
        
        # Comprueba si el día de la cita (Lunes=0) está en la lista de permitidos
        if hora_local.weekday() in dias_laborales_indices:
            citas_filtradas.append(cita)
    # --- FIN DEL FILTRO ---

    # 5. Convertir los objetos de Django en un JSON simple
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
            'paciente_nombre': f"{cita.paciente.nombre} {cita.paciente.apellido}",
            'tratamiento_nombre': cita.tratamiento.nombre if cita.tratamiento else 'N/A',
            'estado': cita.estado or 'Pendiente',
            'duracion': duracion_minutos
        })

    return JsonResponse({'citas': citas_json})