from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q
from .models import (
    Usuario, Paciente, PersonalSalud, PersonalMinsal,
    Campana, Cita, Vacunacion, Vacuna, PuntoVacunacion, Stock, GrupoRiesgo
)
from .forms import (
    LoginForm, RegistroCitaForm, VacunacionForm,
    CampanaForm, RegistroPacienteForm
)
from functools import wraps


# ─── Decoradores de Rol ────────────────────────────────────────────────────────

def rol_requerido(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.rol not in roles and not request.user.is_superuser:
                messages.error(request, "No tienes permiso para acceder a esta sección.")
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator


# ─── Auth ──────────────────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password']
        )
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, "Credenciales incorrectas.")
    return render(request, 'vacunacion/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    user = request.user
    context = {'user': user}

    if user.rol == 'paciente' or (hasattr(user, 'paciente')):
        try:
            paciente = user.paciente
            context['citas'] = Cita.objects.filter(paciente=paciente, cancelada=False).order_by('fecha', 'hora')[:5]
            context['vacunaciones'] = Vacunacion.objects.filter(paciente=paciente).order_by('-fecha')[:5]
            context['total_vacunas'] = Vacunacion.objects.filter(paciente=paciente).count()
        except Paciente.DoesNotExist:
            pass
        return render(request, 'vacunacion/dashboard_paciente.html', context)

    elif user.rol == 'personal_salud':
        context['vacunaciones_hoy'] = Vacunacion.objects.filter(fecha=timezone.now().date()).count()
        context['citas_hoy'] = Cita.objects.filter(fecha=timezone.now().date(), cancelada=False).count()
        context['pacientes'] = Paciente.objects.all()[:5]
        return render(request, 'vacunacion/dashboard_personal.html', context)

    elif user.rol == 'personal_minsal':
        context['total_campanas'] = Campana.objects.count()
        context['total_vacunaciones'] = Vacunacion.objects.count()
        context['total_pacientes'] = Paciente.objects.count()
        context['campanas'] = Campana.objects.order_by('-fechaInicio')[:5]
        return render(request, 'vacunacion/dashboard_minsal.html', context)

    return render(request, 'vacunacion/dashboard_paciente.html', context)


# ─── Paciente ──────────────────────────────────────────────────────────────────

@login_required
@rol_requerido('paciente')
def agendar_cita(request):
    paciente = get_object_or_404(Paciente, usuario=request.user)
    form = RegistroCitaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        cita = form.save(commit=False)
        cita.paciente = paciente
        # Verificar stock
        stock = Stock.objects.filter(
            vacuna=cita.vacuna,
            punto_vacunacion=cita.punto_vacunacion
        ).first()
        if not stock or not stock.verificarDisponibilidad():
            messages.error(request, "No hay stock disponible para esa vacuna en ese punto.")
        else:
            # Verificar horario (no otra cita en mismo slot)
            conflicto = Cita.objects.filter(
                punto_vacunacion=cita.punto_vacunacion,
                fecha=cita.fecha,
                hora=cita.hora,
                cancelada=False
            ).exists()
            if conflicto:
                messages.error(request, "Ya existe una cita en ese horario y punto de vacunación.")
            else:
                cita.save()
                messages.success(request, f"Cita agendada exitosamente para el {cita.fecha} a las {cita.hora}.")
                return redirect('mis_citas')
    return render(request, 'vacunacion/agendar_cita.html', {'form': form})


@login_required
@rol_requerido('paciente')
def mis_citas(request):
    paciente = get_object_or_404(Paciente, usuario=request.user)
    citas = Cita.objects.filter(paciente=paciente).order_by('-fecha', '-hora')
    return render(request, 'vacunacion/mis_citas.html', {'citas': citas})


@login_required
@rol_requerido('paciente')
def cancelar_cita(request, cita_id):
    paciente = get_object_or_404(Paciente, usuario=request.user)
    cita = get_object_or_404(Cita, idCita=cita_id, paciente=paciente)
    cita.cancelarCita()
    messages.success(request, "Cita cancelada correctamente.")
    return redirect('mis_citas')


@login_required
@rol_requerido('paciente')
def mi_historial(request):
    paciente = get_object_or_404(Paciente, usuario=request.user)
    vacunaciones = paciente.obtenerHistorial().select_related('vacuna', 'personal_salud').order_by('-fecha')
    return render(request, 'vacunacion/historial.html', {'vacunaciones': vacunaciones, 'paciente': paciente})


# ─── Personal de Salud ─────────────────────────────────────────────────────────

@login_required
@rol_requerido('personal_salud')
def registrar_vacunacion(request):
    form = VacunacionForm(request.POST or None)
    personal = get_object_or_404(PersonalSalud, usuario=request.user)
    if request.method == 'POST' and form.is_valid():
        vacunacion = form.save(commit=False)
        vacunacion.personal_salud = personal
        vacunacion.save()
        # Reducir stock
        stock = Stock.objects.filter(
            vacuna=vacunacion.vacuna,
            punto_vacunacion__citas__paciente=vacunacion.paciente
        ).first()
        if stock and stock.cantidad > 0:
            stock.cantidad -= 1
            stock.save()
        messages.success(request, "Vacunación registrada exitosamente.")
        return redirect('lista_pacientes')
    return render(request, 'vacunacion/registrar_vacunacion.html', {'form': form})


@login_required
@rol_requerido('personal_salud')
def lista_pacientes(request):
    q = request.GET.get('q', '')
    pacientes = Paciente.objects.all()
    if q:
        pacientes = pacientes.filter(Q(nombre__icontains=q) | Q(rut__icontains=q))
    return render(request, 'vacunacion/lista_pacientes.html', {'pacientes': pacientes, 'q': q})


@login_required
@rol_requerido('personal_salud')
def historial_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    vacunaciones = paciente.obtenerHistorial().select_related('vacuna', 'personal_salud').order_by('-fecha')
    return render(request, 'vacunacion/historial.html', {'vacunaciones': vacunaciones, 'paciente': paciente})


@login_required
@rol_requerido('personal_salud')
def registrar_paciente(request):
    form = RegistroPacienteForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Paciente registrado exitosamente.")
        return redirect('lista_pacientes')
    return render(request, 'vacunacion/registrar_paciente.html', {'form': form})


# ─── Personal MINSAL ──────────────────────────────────────────────────────────

@login_required
@rol_requerido('personal_minsal')
def gestionar_campanas(request):
    campanas = Campana.objects.prefetch_related('grupos_riesgo').order_by('-fechaInicio')
    return render(request, 'vacunacion/campanas.html', {'campanas': campanas})


@login_required
@rol_requerido('personal_minsal')
def crear_campana(request):
    form = CampanaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        campana = form.save(commit=False)
        minsal = get_object_or_404(PersonalMinsal, usuario=request.user)
        campana.gestionada_por = minsal
        campana.save()
        form.save_m2m()
        messages.success(request, f"Campaña '{campana.nombre}' creada exitosamente.")
        return redirect('gestionar_campanas')
    return render(request, 'vacunacion/crear_campana.html', {'form': form})


@login_required
@rol_requerido('personal_minsal')
def eliminar_campana(request, campana_id):
    campana = get_object_or_404(Campana, pk=campana_id)
    campana.eliminarCampana()
    messages.success(request, "Campaña eliminada.")
    return redirect('gestionar_campanas')


@login_required
@rol_requerido('personal_minsal')
def reporte_vacunaciones(request):
    vacunaciones = Vacunacion.objects.select_related(
        'paciente', 'vacuna', 'personal_salud', 'campana'
    ).order_by('-fecha')
    total = vacunaciones.count()
    return render(request, 'vacunacion/reporte.html', {'vacunaciones': vacunaciones, 'total': total})


# ─── API para stock (AJAX) ────────────────────────────────────────────────────

@login_required
def verificar_stock_ajax(request):
    vacuna_id = request.GET.get('vacuna_id')
    punto_id = request.GET.get('punto_id')
    if vacuna_id and punto_id:
        stock = Stock.objects.filter(vacuna_id=vacuna_id, punto_vacunacion_id=punto_id).first()
        disponible = stock.verificarDisponibilidad() if stock else False
        cantidad = stock.cantidad if stock else 0
        return JsonResponse({'disponible': disponible, 'cantidad': cantidad})
    return JsonResponse({'disponible': False, 'cantidad': 0})
