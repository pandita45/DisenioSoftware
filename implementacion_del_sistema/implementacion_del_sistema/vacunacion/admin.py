from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Usuario, PersonalMinsal, PersonalSalud, Paciente,
    Campana, GrupoRiesgo, Cita, Vacunacion, Vacuna,
    PuntoVacunacion, Stock
)


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'rut', 'rol', 'email', 'is_active')
    list_filter = ('rol', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {'fields': ('rol', 'rut')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Adicional', {'fields': ('rol', 'rut')}),
    )


@admin.register(PersonalMinsal)
class PersonalMinsalAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'rut')


@admin.register(PersonalSalud)
class PersonalSaludAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'rut', 'rol')


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'rut', 'fechaNacimiento')
    search_fields = ('nombre', 'rut')


@admin.register(Campana)
class CampanaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fechaInicio', 'fechaTermino', 'gestionada_por')
    filter_horizontal = ('grupos_riesgo',)


@admin.register(GrupoRiesgo)
class GrupoRiesgoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('idCita', 'paciente', 'vacuna', 'punto_vacunacion', 'fecha', 'hora', 'correo', 'cancelada', 'recordatorio_enviado')
    list_filter = ('cancelada', 'recordatorio_enviado', 'fecha')


@admin.register(Vacunacion)
class VacunacionAdmin(admin.ModelAdmin):
    list_display = ('idVacunacion', 'paciente', 'vacuna', 'personal_salud', 'fecha')
    list_filter = ('fecha', 'vacuna')


@admin.register(Vacuna)
class VacunaAdmin(admin.ModelAdmin):
    list_display = ('idTipo', 'nombre')


@admin.register(PuntoVacunacion)
class PuntoVacunacionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'direccion')


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('vacuna', 'punto_vacunacion', 'cantidad')
