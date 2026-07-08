from django.core.management.base import BaseCommand
from vacunacion.models import Paciente, Vacuna, Cita
from django.db import transaction
from django.utils import timezone


class Command(BaseCommand):
    help = 'Limpia pacientes de prueba, unifica vacunas repetidas y actualiza citas vencidas'

    def handle(self, *args, **options):
        with transaction.atomic():
            pacientes_prueba = Paciente.objects.filter(usuario__username__in=['paciente1','paciente2','paciente3','paciente4'])
            usuarios_eliminados = 0
            for paciente in pacientes_prueba:
                if paciente.usuario_id:
                    paciente.usuario.delete()
                    usuarios_eliminados += 1
            self.stdout.write(self.style.SUCCESS(f'Pacientes de prueba eliminados: {pacientes_prueba.count()}'))

            vacunas = Vacuna.objects.all().order_by('nombre', 'idTipo')
            vacunas_por_nombre = {}
            for vacuna in vacunas:
                nombre = vacuna.nombre.strip()
                if nombre not in vacunas_por_nombre:
                    vacunas_por_nombre[nombre] = vacuna
                else:
                    for cita in Cita.objects.filter(vacuna=vacuna):
                        cita.vacuna = vacunas_por_nombre[nombre]
                        cita.save(update_fields=['vacuna'])
                    vacuna.delete()
            self.stdout.write(self.style.SUCCESS('Vacunas duplicadas unificadas'))

            hoy = timezone.now().date()
            citas_vencidas = Cita.objects.filter(estado='agendada', cancelada=False, fecha__lt=hoy)
            actualizadas = 0
            for cita in citas_vencidas:
                cita.estado = 'ausente'
                cita.save(update_fields=['estado'])
                actualizadas += 1
            self.stdout.write(self.style.SUCCESS(f'Citas vencidas actualizadas: {actualizadas}'))
