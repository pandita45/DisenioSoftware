from django import forms
import datetime
from django.utils import timezone
from .models import Cita, Vacunacion, Campana, Paciente, Usuario, Vacuna


class LoginForm(forms.Form):
    username = forms.CharField(label="Usuario", widget=forms.TextInput(attrs={'placeholder': 'Usuario o RUT'}))
    password = forms.CharField(label="Contrasena", widget=forms.PasswordInput(attrs={'placeholder': 'Contrasena'}))


class RegistroCitaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        hoy = timezone.now().date()
        vacunas_disponibles = Campana.vacunas_activas(hoy)

        vacuna_id = None
        if self.data.get('vacuna'):
            vacuna_id = self.data.get('vacuna')
        elif getattr(self.instance, 'vacuna_id', None):
            vacuna_id = self.instance.vacuna_id

        if vacuna_id:
            vacuna_obj = Vacuna.objects.filter(pk=vacuna_id).first()
            if vacuna_obj:
                vacuna_ids = list(vacunas_disponibles.values_list('pk', flat=True))
                if vacuna_obj.pk not in vacuna_ids:
                    vacuna_ids.append(vacuna_obj.pk)
                vacunas_disponibles = Vacuna.objects.filter(pk__in=vacuna_ids)

        self.fields['vacuna'].queryset = vacunas_disponibles.distinct()

    class Meta:
        model = Cita
        fields = ['punto_vacunacion', 'vacuna', 'correo', 'fecha', 'hora']
        widgets = {
            'fecha': forms.DateInput(attrs={
                'type': 'date',
                'min': datetime.date.today().isoformat()
            }),
            'hora': forms.TimeInput(attrs={'type': 'time'}),
        }
        labels = {
            'punto_vacunacion': 'Punto de Vacunacion',
            'vacuna': 'Vacuna',
            'correo': 'Correo para notificaciones',
            'fecha': 'Fecha',
            'hora': 'Hora',
        }

    def clean_fecha(self):
        fecha = self.cleaned_data.get('fecha')
        if fecha and fecha < datetime.date.today():
            raise forms.ValidationError("No puedes agendar una cita en una fecha pasada.")
        return fecha

    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha')
        hora = cleaned_data.get('hora')
        if fecha and hora and fecha < datetime.date.today():
            self.add_error('fecha', 'No puedes agendar una cita en una fecha pasada.')
        return cleaned_data


class VacunacionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        hoy = timezone.now().date()
        vacunas_disponibles = Campana.vacunas_activas(hoy)

        vacuna_id = None
        if self.data.get('vacuna'):
            vacuna_id = self.data.get('vacuna')
        elif getattr(self.instance, 'vacuna_id', None):
            vacuna_id = self.instance.vacuna_id

        if vacuna_id:
            vacuna_obj = Vacuna.objects.filter(pk=vacuna_id).first()
            if vacuna_obj:
                vacuna_ids = list(vacunas_disponibles.values_list('pk', flat=True))
                if vacuna_obj.pk not in vacuna_ids:
                    vacuna_ids.append(vacuna_obj.pk)
                vacunas_disponibles = Vacuna.objects.filter(pk__in=vacuna_ids)

        self.fields['vacuna'].queryset = vacunas_disponibles.distinct()

        citas_disponibles = Cita.objects.filter(estado='agendada')
        cita_inicial = self.initial.get('cita')
        if cita_inicial is None and getattr(self.instance, 'pk', None):
            cita_inicial = self.instance.cita
        if cita_inicial is not None:
            cita_pk = cita_inicial.pk if hasattr(cita_inicial, 'pk') else cita_inicial
            citas_disponibles = citas_disponibles | Cita.objects.filter(pk=cita_pk)
        self.fields['cita'].queryset = citas_disponibles.order_by('fecha', 'hora', 'idCita')

    class Meta:
        model = Vacunacion
        fields = ['cita', 'paciente', 'vacuna', 'campana', 'fecha', 'hora']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'hora': forms.TimeInput(attrs={'type': 'time'}),
        }
        labels = {
            'paciente': 'Paciente',
            'vacuna': 'Vacuna Administrada',
            'cita': 'Cita Asociada (opcional)',
            'campana': 'Campana (opcional)',
            'fecha': 'Fecha',
            'hora': 'Hora',
        }


class CampanaForm(forms.ModelForm):
    class Meta:
        model = Campana
        fields = ['nombre', 'fechaInicio', 'fechaTermino', 'vacuna', 'grupos_riesgo']
        widgets = {
            'fechaInicio': forms.DateInput(attrs={'type': 'date'}),
            'fechaTermino': forms.DateInput(attrs={'type': 'date'}),
            'grupos_riesgo': forms.CheckboxSelectMultiple(),
        }
        labels = {
            'nombre': 'Nombre de la Campana',
            'fechaInicio': 'Fecha de Inicio',
            'fechaTermino': 'Fecha de Termino',
            'vacuna': 'Vacuna asociada',
            'grupos_riesgo': 'Grupos de Riesgo',
        }

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fechaInicio')
        fecha_termino = cleaned_data.get('fechaTermino')

        if fecha_inicio and fecha_termino and fecha_inicio > fecha_termino:
            raise forms.ValidationError('La fecha de término no puede ser anterior a la fecha de inicio.')

        return cleaned_data


class RegistroPacienteForm(forms.Form):
    rut = forms.CharField(max_length=12, label="RUT")
    nombre = forms.CharField(max_length=100, label="Nombre Completo")
    fecha_nacimiento = forms.DateField(label="Fecha de Nacimiento", widget=forms.DateInput(attrs={'type': 'date'}))
    username = forms.CharField(max_length=50, label="Nombre de Usuario")
    password = forms.CharField(label="Contrasena", widget=forms.PasswordInput())

    def save(self):
        data = self.cleaned_data
        user = Usuario.objects.create_user(
            username=data['username'],
            password=data['password'],
            rol='paciente',
            rut=data['rut'],
        )
        Paciente.objects.create(
            usuario=user,
            rut=data['rut'],
            nombre=data['nombre'],
            fechaNacimiento=data['fecha_nacimiento'],
        )
        return user