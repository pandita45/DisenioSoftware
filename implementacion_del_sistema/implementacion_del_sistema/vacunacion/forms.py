from django import forms
import datetime
from .models import Cita, Vacunacion, Campana, Paciente, Usuario


class LoginForm(forms.Form):
    username = forms.CharField(label="Usuario", widget=forms.TextInput(attrs={'placeholder': 'Usuario o RUT'}))
    password = forms.CharField(label="Contrasena", widget=forms.PasswordInput(attrs={'placeholder': 'Contrasena'}))


class RegistroCitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['punto_vacunacion', 'vacuna', 'fecha', 'hora']
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
        if fecha and hora:
            ahora = datetime.datetime.now()
            if fecha == datetime.date.today() and hora < ahora.time():
                self.add_error('hora', f"Son las {ahora.strftime('%H:%M')}, no puedes agendar a una hora que ya paso.")
        return cleaned_data


class VacunacionForm(forms.ModelForm):
    class Meta:
        model = Vacunacion
        fields = ['paciente', 'vacuna', 'cita', 'campana', 'fecha', 'hora']
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
        fields = ['nombre', 'fechaInicio', 'fechaTermino', 'grupos_riesgo']
        widgets = {
            'fechaInicio': forms.DateInput(attrs={'type': 'date'}),
            'fechaTermino': forms.DateInput(attrs={'type': 'date'}),
            'grupos_riesgo': forms.CheckboxSelectMultiple(),
        }
        labels = {
            'nombre': 'Nombre de la Campana',
            'fechaInicio': 'Fecha de Inicio',
            'fechaTermino': 'Fecha de Termino',
            'grupos_riesgo': 'Grupos de Riesgo',
        }


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