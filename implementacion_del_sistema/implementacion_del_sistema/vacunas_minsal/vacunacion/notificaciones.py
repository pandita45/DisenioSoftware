from django.core.mail import send_mail
from django.conf import settings


def notificar_registro(nombre, correo):
    asunto = "Registro exitoso — Sistema de Vacunacion MINSAL"
    mensaje = f"""Estimado/a {nombre},

Se le ha registrado correctamente en el sistema de vacunacion del MINSAL.

Si no ha sido usted, favor contactarse inmediatamente con MINSAL (600 360 7777)
O ir a la comisaria mas cercana por asesoramiento.

Atentamente,
Sistema VacunaChile — MINSAL
"""
    try:
        send_mail(asunto, mensaje, settings.DEFAULT_FROM_EMAIL, [correo])
        return True
    except Exception as e:
        print(f"Error enviando correo de registro: {e}")
        return False


def notificar_cita(nombre, correo, fecha, hora, punto, vacuna):
    asunto = "Confirmacion de Cita — Sistema de Vacunacion MINSAL"
    mensaje = f"""Estimado/a {nombre},

Su cita de vacunacion ha sido agendada exitosamente.

Detalles de la cita:
  - Vacuna:             {vacuna}
  - Fecha:              {fecha}
  - Hora:               {hora}
  - Punto de vacunacion: {punto}

Recuerde presentarse con su cedula de identidad.

Si no ha sido usted quien agendo esta cita, favor contactarse inmediatamente
con MINSAL (600 360 7777) o ir a la comisaria mas cercana por asesoramiento.

Atentamente,
Sistema VacunaChile — MINSAL
"""
    try:
        send_mail(asunto, mensaje, settings.DEFAULT_FROM_EMAIL, [correo])
        return True
    except Exception as e:
        print(f"Error enviando correo de cita: {e}")
        return False