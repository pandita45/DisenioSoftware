from django.db import models
from django.contrib.auth.models import AbstractUser


class Usuario(AbstractUser):
    ROLES = [
        ('paciente', 'Paciente'),
        ('personal_salud', 'Personal de Salud'),
        ('personal_minsal', 'Personal MINSAL'),
    ]
    rol = models.CharField(max_length=20, choices=ROLES, default='paciente')
    rut = models.CharField(max_length=12, unique=True, null=True, blank=True)

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_rol_display})"


class PersonalMinsal(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='minsal')
    rut = models.CharField(max_length=12, unique=True)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Personal MINSAL"
        verbose_name_plural = "Personal MINSAL"


class GrupoRiesgo(models.Model):
    idGroup = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Grupo de Riesgo"
        verbose_name_plural = "Grupos de Riesgo"


class Campana(models.Model):
    idCampana = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150)
    fechaInicio = models.DateField()
    fechaTermino = models.DateField()
    grupos_riesgo = models.ManyToManyField(GrupoRiesgo, blank=True, related_name='campanas')
    gestionada_por = models.ForeignKey(
        PersonalMinsal, on_delete=models.SET_NULL, null=True, related_name='campanas'
    )

    def registrarCampana(self):
        self.save()

    def eliminarCampana(self):
        self.delete()

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Campaña"
        verbose_name_plural = "Campañas"


class Paciente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='paciente')
    rut = models.CharField(max_length=12, unique=True)
    nombre = models.CharField(max_length=100)
    fechaNacimiento = models.DateField()
    campanas = models.ManyToManyField(Campana, blank=True, related_name='pacientes')
    grupos_riesgo = models.ManyToManyField(GrupoRiesgo, blank=True, related_name='pacientes')

    def obtenerHistorial(self):
        return Vacunacion.objects.filter(paciente=self)

    def __str__(self):
        return f"{self.nombre} ({self.rut})"


class PersonalSalud(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='personal_salud')
    rut = models.CharField(max_length=12, unique=True)
    nombre = models.CharField(max_length=100)
    rol = models.CharField(max_length=80)

    def registrarPaciente(self, paciente):
        paciente.save()

    def __str__(self):
        return f"{self.nombre} - {self.rol}"

    class Meta:
        verbose_name = "Personal de Salud"
        verbose_name_plural = "Personal de Salud"


class Vacuna(models.Model):
    idTipo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class PuntoVacunacion(models.Model):
    idPunto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.nombre} - {self.direccion}"

    class Meta:
        verbose_name = "Punto de Vacunacion"
        verbose_name_plural = "Puntos de Vacunacion"


class Stock(models.Model):
    vacuna = models.ForeignKey(Vacuna, on_delete=models.CASCADE, related_name='stocks')
    punto_vacunacion = models.ForeignKey(PuntoVacunacion, on_delete=models.CASCADE, related_name='stocks')
    cantidad = models.IntegerField(default=0)

    def actualizarStock(self, cantidad):
        self.cantidad = cantidad
        self.save()

    def verificarDisponibilidad(self):
        return self.cantidad > 0

    def __str__(self):
        return f"{self.vacuna.nombre} en {self.punto_vacunacion.nombre}: {self.cantidad}"


class Cita(models.Model):
    idCita = models.AutoField(primary_key=True)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='citas')
    punto_vacunacion = models.ForeignKey(PuntoVacunacion, on_delete=models.CASCADE, related_name='citas')
    vacuna = models.ForeignKey(Vacuna, on_delete=models.CASCADE, related_name='citas')
    fecha = models.DateField()
    hora = models.TimeField()
    cancelada = models.BooleanField(default=False)

    def agendarCita(self):
        stock = Stock.objects.filter(
            vacuna=self.vacuna,
            punto_vacunacion=self.punto_vacunacion
        ).first()
        if stock and stock.verificarDisponibilidad():
            self.save()
            return True
        return False

    def cancelarCita(self):
        self.cancelada = True
        self.save()

    def __str__(self):
        return f"Cita {self.idCita} - {self.paciente.nombre} el {self.fecha}"


class Vacunacion(models.Model):
    idVacunacion = models.AutoField(primary_key=True)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='vacunaciones')
    personal_salud = models.ForeignKey(PersonalSalud, on_delete=models.SET_NULL, null=True, related_name='vacunaciones')
    vacuna = models.ForeignKey(Vacuna, on_delete=models.CASCADE, related_name='vacunaciones')
    cita = models.OneToOneField(Cita, on_delete=models.SET_NULL, null=True, blank=True, related_name='vacunacion')
    campana = models.ForeignKey(Campana, on_delete=models.SET_NULL, null=True, blank=True, related_name='vacunaciones')
    fecha = models.DateField()
    hora = models.TimeField()

    def obtenerVacunaRecibida(self):
        return self.vacuna.nombre

    def __str__(self):
        return f"Vacunacion {self.idVacunacion} - {self.paciente.nombre} ({self.vacuna.nombre})"

    class Meta:
        verbose_name = "Vacunacion"
        verbose_name_plural = "Vacunaciones"