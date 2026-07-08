from django import forms
import datetime
from .models import Cita, Vacunacion, Campana, Paciente, Usuario, Stock


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
            'fecha': forms.DateInput(attrs={
                'type': 'date',
                'max': datetime.date.today().isoformat()
            }),
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cita'].queryset = Cita.objects.filter(
            cancelada=False,
            vacunacion__isnull=True
        )

    def clean_fecha(self):
        fecha = self.cleaned_data.get('fecha')
        if fecha and fecha > datetime.date.today():
            raise forms.ValidationError("No puedes registrar una vacunacion con fecha futura.")
        return fecha

    def clean(self):
        cleaned_data = super().clean()
        paciente = cleaned_data.get('paciente')
        vacuna = cleaned_data.get('vacuna')
        fecha = cleaned_data.get('fecha')
        if paciente and vacuna and fecha:
            duplicado = Vacunacion.objects.filter(
                paciente=paciente,
                vacuna=vacuna,
                fecha=fecha
            ).exists()
            if duplicado:
                raise forms.ValidationError(
                    f"El paciente {paciente.nombre} ya tiene registrada una vacunacion de {vacuna.nombre} el dia {fecha}."
                )
        return cleaned_data


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

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fechaInicio')
        fecha_termino = cleaned_data.get('fechaTermino')
        if fecha_inicio and fecha_termino:
            if fecha_termino < fecha_inicio:
                raise forms.ValidationError(
                    "La fecha de termino no puede ser anterior a la fecha de inicio."
                )
        return cleaned_data


class RegistroPacienteForm(forms.Form):
    rut = forms.CharField(
        max_length=12,
        label="RUT",
        help_text="Ingresa solo numeros y digito verificador. Ej: 143455674",
        widget=forms.TextInput(attrs={
            'placeholder': 'Ej: 143455674',
            'maxlength': '10',
        })
    )
    nombre = forms.CharField(max_length=100, label="Nombre Completo")
    correo = forms.EmailField(
        label="Correo Electronico",
        widget=forms.EmailInput(attrs={'placeholder': 'ejemplo@correo.com'})
    )
    fecha_nacimiento = forms.DateField(
        label="Fecha de Nacimiento",
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    username = forms.CharField(max_length=50, label="Nombre de Usuario")
    password = forms.CharField(label="Contrasena", widget=forms.PasswordInput())
    password_confirmar = forms.CharField(label="Confirmar Contrasena", widget=forms.PasswordInput())

    def clean_rut(self):
        rut = self.cleaned_data.get('rut').strip().replace('.', '').replace('-', '')

        if not rut[:-1].isdigit():
            raise forms.ValidationError("El RUT solo debe contener numeros y digito verificador.")
        if not (rut[-1].isdigit() or rut[-1].lower() == 'k'):
            raise forms.ValidationError("El digito verificador solo puede ser un numero o la letra K.")
        if len(rut) < 7 or len(rut) > 10:
            raise forms.ValidationError("El RUT debe tener entre 7 y 10 caracteres.")

        cuerpo = rut[:-1]
        dv_ingresado = rut[-1].upper()

        if len(cuerpo) == 7:
            rut_formateado = f"{cuerpo[0]}.{cuerpo[1:4]}.{cuerpo[4:]}-{dv_ingresado}"
        elif len(cuerpo) == 8:
            rut_formateado = f"{cuerpo[0:2]}.{cuerpo[2:5]}.{cuerpo[5:]}-{dv_ingresado}"
        else:
            rut_formateado = f"{cuerpo}-{dv_ingresado}"

        if Paciente.objects.filter(rut=rut_formateado).exists():
            raise forms.ValidationError(f"Ya existe un paciente con el RUT {rut_formateado}.")

        return rut_formateado

    def clean_correo(self):
        correo = self.cleaned_data.get('correo')
        if Usuario.objects.filter(email=correo).exists():
            raise forms.ValidationError("Ya existe una cuenta con ese correo electronico.")
        return correo

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if Usuario.objects.filter(username=username).exists():
            raise forms.ValidationError(f"El usuario '{username}' ya esta en uso.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirmar = cleaned_data.get('password_confirmar')
        if password and password_confirmar and password != password_confirmar:
            self.add_error('password_confirmar', "Las contrasenas no coinciden.")
        return cleaned_data

    def save(self):
        data = self.cleaned_data
        user = Usuario.objects.create_user(
            username=data['username'],
            password=data['password'],
            email=data['correo'],
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