from django.core.management.base import BaseCommand
from django.utils import timezone
from vacunacion.models import (
    Usuario, PersonalMinsal, PersonalSalud, Paciente,
    GrupoRiesgo, Campana, Vacuna, PuntoVacunacion, Stock, Cita, Vacunacion
)
import datetime


class Command(BaseCommand):
    help = 'Poblar la base de datos con datos de prueba'

    def handle(self, *args, **kwargs):
        self.stdout.write("🌱 Creando datos de prueba...")

        # ── Grupos de Riesgo ──
        adulto_mayor, _ = GrupoRiesgo.objects.get_or_create(
            nombre="Adulto Mayor", defaults={'descripcion': 'Personas mayores de 65 años'}
        )
        embarazadas, _ = GrupoRiesgo.objects.get_or_create(
            nombre="Embarazadas", defaults={'descripcion': 'Mujeres en estado de gestación'}
        )
        cronicos, _ = GrupoRiesgo.objects.get_or_create(
            nombre="Enfermos Crónicos", defaults={'descripcion': 'Personas con enfermedades crónicas'}
        )

        # ── Vacunas ──
        influenza, _ = Vacuna.objects.get_or_create(nombre="Influenza")
        covid, _ = Vacuna.objects.get_or_create(nombre="COVID-19 Bivalente")
        hepatitis, _ = Vacuna.objects.get_or_create(nombre="Hepatitis B")
        tetano, _ = Vacuna.objects.get_or_create(nombre="Tétanos-Difteria")

        # ── Puntos de Vacunación ──
        cesfam_bio, _ = PuntoVacunacion.objects.get_or_create(
            nombre="CESFAM Biobío", defaults={'direccion': 'Av. Costanera 1234, Concepción'}
        )
        hosp_talcahuano, _ = PuntoVacunacion.objects.get_or_create(
            nombre="Hospital Talcahuano", defaults={'direccion': 'Calle O\'Higgins 555, Talcahuano'}
        )
        cesfam_penco, _ = PuntoVacunacion.objects.get_or_create(
            nombre="CESFAM Penco", defaults={'direccion': 'Calle Balmaceda 200, Penco'}
        )

        # ── Stock ──
        for vacuna in [influenza, covid, hepatitis, tetano]:
            for punto in [cesfam_bio, hosp_talcahuano, cesfam_penco]:
                Stock.objects.get_or_create(
                    vacuna=vacuna,
                    punto_vacunacion=punto,
                    defaults={'cantidad': 100}
                )

        # ── Usuario MINSAL ──
        if not Usuario.objects.filter(username='minsal1').exists():
            u_minsal = Usuario.objects.create_user(
                username='minsal1', password='pass1234',
                first_name='Carmen', last_name='Vásquez',
                email='carmen.vasquez@minsal.cl', rol='personal_minsal', rut='9.111.222-3'
            )
            PersonalMinsal.objects.create(usuario=u_minsal, rut='9.111.222-3', nombre='Carmen Vásquez')
            self.stdout.write("  ✓ Usuario MINSAL: minsal1 / pass1234")

        # ── Campaña ──
        minsal_obj = PersonalMinsal.objects.first()
        campana_influenza, _ = Campana.objects.get_or_create(
            nombre="Campaña Influenza 2026",
            defaults={
                'fechaInicio': datetime.date(2026, 4, 1),
                'fechaTermino': datetime.date(2026, 6, 30),
                'gestionada_por': minsal_obj,
            }
        )
        campana_influenza.grupos_riesgo.add(adulto_mayor, embarazadas, cronicos)

        campana_covid, _ = Campana.objects.get_or_create(
            nombre="Refuerzo COVID-19 Otoño 2026",
            defaults={
                'fechaInicio': datetime.date(2026, 5, 1),
                'fechaTermino': datetime.date(2026, 7, 31),
                'gestionada_por': minsal_obj,
            }
        )
        campana_covid.grupos_riesgo.add(adulto_mayor, cronicos)

        # ── Personal de Salud ──
        if not Usuario.objects.filter(username='enfermera1').exists():
            u_enf = Usuario.objects.create_user(
                username='enfermera1', password='pass1234',
                first_name='Valentina', last_name='Morales',
                email='v.morales@cesfam.cl', rol='personal_salud', rut='12.345.678-9'
            )
            PersonalSalud.objects.create(
                usuario=u_enf, rut='12.345.678-9',
                nombre='Valentina Morales', rol='Enfermera'
            )
            self.stdout.write("  ✓ Personal Salud: enfermera1 / pass1234")

        if not Usuario.objects.filter(username='medico1').exists():
            u_med = Usuario.objects.create_user(
                username='medico1', password='pass1234',
                first_name='Rodrigo', last_name='Sepúlveda',
                email='r.sepulveda@hospital.cl', rol='personal_salud', rut='11.222.333-4'
            )
            PersonalSalud.objects.create(
                usuario=u_med, rut='11.222.333-4',
                nombre='Dr. Rodrigo Sepúlveda', rol='Médico General'
            )
            self.stdout.write("  ✓ Personal Salud: medico1 / pass1234")

        # ── Pacientes ──

        pacientes_data = [
    ('paciente1', 'pass1234', 'Ana', 'González', '15.234.567-8', datetime.date(1990, 3, 15), 'ana.gonzalez@gmail.com'),
    ('paciente2', 'pass1234', 'Carlos', 'Muñoz', '16.789.012-3', datetime.date(1955, 7, 22), 'carlos.munoz@gmail.com'),
    ('paciente3', 'pass1234', 'María', 'Soto', '14.321.098-7', datetime.date(1978, 11, 5), 'maria.soto@gmail.com'),
    ('paciente4', 'pass1234', 'Jorge', 'Ramírez', '17.654.321-0', datetime.date(2000, 1, 30), 'jorge.ramirez@gmail.com'),
]
        

        paciente_objs = []
        for username, password, nombre, apellido, rut, fecha, email in pacientes_data:
            if not Usuario.objects.filter(username=username).exists():
                u = Usuario.objects.create_user(
                    username=username, password=password,
                    first_name=nombre, last_name=apellido,
                    email=email, rol='paciente', rut=rut
                )
                p = Paciente.objects.create(
                    usuario=u, rut=rut,
                    nombre=f"{nombre} {apellido}",
                    fechaNacimiento=fecha
                )
                paciente_objs.append(p)
                self.stdout.write(f"  ✓ Paciente: {username} / pass1234")
            else:
                try:
                    paciente_objs.append(Paciente.objects.get(rut=rut))
                except Paciente.DoesNotExist:
                    pass

        # Asignar grupos de riesgo
        if len(paciente_objs) >= 2:
            paciente_objs[1].grupos_riesgo.add(adulto_mayor)  # Carlos es adulto mayor
        if len(paciente_objs) >= 3:
            paciente_objs[2].grupos_riesgo.add(cronicos)

        # ── Vacunaciones de ejemplo ──
        personal = PersonalSalud.objects.first()
        if personal and paciente_objs:
            for i, (paciente, vacuna) in enumerate([
                (paciente_objs[0], influenza),
                (paciente_objs[1], covid),
                (paciente_objs[1], influenza),
                (paciente_objs[2], tetano),
            ]):
                Vacunacion.objects.get_or_create(
                    paciente=paciente,
                    vacuna=vacuna,
                    defaults={
                        'personal_salud': personal,
                        'campana': campana_influenza if vacuna == influenza else campana_covid,
                        'fecha': datetime.date(2026, 5, 10 + i),
                        'hora': datetime.time(9 + i, 0),
                    }
                )

        # ── Citas de ejemplo ──
        if paciente_objs:
            Cita.objects.get_or_create(
                paciente=paciente_objs[0],
                vacuna=covid,
                punto_vacunacion=cesfam_bio,
                fecha=datetime.date(2026, 6, 20),
                defaults={'hora': datetime.time(10, 30)}
            )
            if len(paciente_objs) > 3:
                Cita.objects.get_or_create(
                    paciente=paciente_objs[3],
                    vacuna=hepatitis,
                    punto_vacunacion=cesfam_penco,
                    fecha=datetime.date(2026, 6, 25),
                    defaults={'hora': datetime.time(11, 0)}
                )

        self.stdout.write(self.style.SUCCESS("\n✅ Base de datos poblada exitosamente."))
        self.stdout.write("\n📋 Credenciales disponibles:")
        self.stdout.write("  🏛️  MINSAL:         minsal1 / pass1234")
        self.stdout.write("  🩺  Enfermera:      enfermera1 / pass1234")
        self.stdout.write("  🩺  Médico:         medico1 / pass1234")
        self.stdout.write("  👤  Paciente 1:     paciente1 / pass1234 (Ana González)")
        self.stdout.write("  👤  Paciente 2:     paciente2 / pass1234 (Carlos Muñoz)")
        self.stdout.write("  👤  Paciente 3:     paciente3 / pass1234 (María Soto)")
        self.stdout.write("  👤  Paciente 4:     paciente4 / pass1234 (Jorge Ramírez)")
