from datetime import date, time, timedelta
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from .forms import RegistroCitaForm, VacunacionForm
from .models import Campana, Cita, GrupoRiesgo, Paciente, PersonalMinsal, PersonalSalud, PuntoVacunacion, Usuario, Vacuna, Vacunacion, Stock
from .views import enviar_recordatorios_citas


class CrearCampanaViewTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username='minsal_user',
            password='12345678',
            rol='personal_minsal',
            rut='11111111-1',
        )
        self.personal_minsal = PersonalMinsal.objects.create(
            usuario=self.usuario,
            rut='11111111-1',
            nombre='Personal MINSAL',
        )
        self.grupo = GrupoRiesgo.objects.create(
            nombre='Adulto Mayor',
            descripcion='Personas mayores de 60 años',
        )

    def test_crear_campana_muestra_formulario_y_guarda(self):
        self.client.force_login(self.usuario)

        response = self.client.get(reverse('crear_campana'))
        self.assertEqual(response.status_code, 200)

        vacuna = Vacuna.objects.create(nombre='Influenza')
        response = self.client.post(
            reverse('crear_campana'),
            {
                'nombre': 'Campaña de invierno',
                'fechaInicio': '2026-07-10',
                'fechaTermino': '2026-07-20',
                'grupos_riesgo': [self.grupo.idGroup],
                'vacuna': vacuna.idTipo,
            },
        )

        self.assertEqual(response.status_code, 302)
        campana = Campana.objects.get(nombre='Campaña de invierno')
        self.assertEqual(campana.gestionada_por, self.personal_minsal)
        self.assertEqual(campana.vacuna, vacuna)
        self.assertIn(self.grupo, campana.grupos_riesgo.all())

    def test_formularios_solo_muestran_vacunas_de_campanas_activas(self):
        vacuna_activa = Vacuna.objects.create(nombre='Covid-19')
        vacuna_inactiva = Vacuna.objects.create(nombre='SARS')
        Campana.objects.create(
            nombre='Campaña activa',
            fechaInicio=date.today().replace(day=1),
            fechaTermino=date.today().replace(day=28),
            vacuna=vacuna_activa,
            gestionada_por=self.personal_minsal,
        )
        Campana.objects.create(
            nombre='Campaña inactiva',
            fechaInicio=date.today().replace(day=1),
            fechaTermino=date.today().replace(day=2),
            vacuna=vacuna_inactiva,
            gestionada_por=self.personal_minsal,
        )

        cita_form = RegistroCitaForm()
        vacunacion_form = VacunacionForm()

        self.assertEqual(list(cita_form.fields['vacuna'].queryset), [vacuna_activa])
        self.assertEqual(list(vacunacion_form.fields['vacuna'].queryset), [vacuna_activa])

    def test_reporte_muestra_resumen_por_campana(self):
        vacuna = Vacuna.objects.create(nombre='Triple viral')
        campana = Campana.objects.create(
            nombre='Campaña reporte',
            fechaInicio=date.today(),
            fechaTermino=date.today(),
            vacuna=vacuna,
            gestionada_por=self.personal_minsal,
        )
        paciente = Paciente.objects.create(
            usuario=Usuario.objects.create_user(username='paciente_reporte', password='12345678', rol='paciente', rut='22222222-2'),
            rut='22222222-2',
            nombre='Paciente Reporte',
            fechaNacimiento=date(1990, 1, 1),
        )
        personal = PersonalSalud.objects.create(
            usuario=Usuario.objects.create_user(username='salud_reporte', password='12345678', rol='personal_salud', rut='33333333-3'),
            rut='33333333-3',
            nombre='Personal Salud',
            rol='Enfermero',
        )
        Vacunacion.objects.create(
            paciente=paciente,
            personal_salud=personal,
            vacuna=vacuna,
            campana=campana,
            fecha=date.today(),
            hora=time(9, 0),
        )

        self.client.force_login(self.usuario)
        response = self.client.get(reverse('reporte_vacunaciones'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Reporte por campañas')
        self.assertContains(response, campana.nombre)

    def test_reporte_permite_ver_historial_completo_de_una_campana(self):
        vacuna = Vacuna.objects.create(nombre='Rotavirus')
        campana = Campana.objects.create(
            nombre='Campaña historial',
            fechaInicio=date.today(),
            fechaTermino=date.today(),
            vacuna=vacuna,
            gestionada_por=self.personal_minsal,
        )
        paciente = Paciente.objects.create(
            usuario=Usuario.objects.create_user(username='paciente_historial', password='12345678', rol='paciente', rut='44444444-4'),
            rut='44444444-4',
            nombre='Paciente Historial',
            fechaNacimiento=date(1992, 2, 2),
        )
        Vacunacion.objects.create(
            paciente=paciente,
            vacuna=vacuna,
            campana=campana,
            fecha=date.today(),
            hora=time(10, 0),
        )

        self.client.force_login(self.usuario)
        response = self.client.get(reverse('reporte_campana', args=[campana.idCampana]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Historial completo')
        self.assertContains(response, paciente.nombre)

    def test_estados_de_cita_se_actualizan_según_el_flujo(self):
        paciente = Paciente.objects.create(
            usuario=Usuario.objects.create_user(username='paciente_estado', password='12345678', rol='paciente', rut='55555555-5'),
            rut='55555555-5',
            nombre='Paciente Estado',
            fechaNacimiento=date(1990, 1, 1),
        )
        punto = PuntoVacunacion.objects.create(nombre='Centro', direccion='Dirección 1')
        vacuna = Vacuna.objects.create(nombre='Meningitis')
        cita = Cita.objects.create(
            paciente=paciente,
            punto_vacunacion=punto,
            vacuna=vacuna,
            fecha=date.today(),
            hora=time(8, 0),
        )

        self.assertEqual(cita.estado, 'agendada')

        cita.cancelarCita()
        self.assertEqual(cita.estado, 'cancelada')

        cita = Cita.objects.create(
            paciente=paciente,
            punto_vacunacion=punto,
            vacuna=vacuna,
            fecha=date.today() - date.resolution,
            hora=time(8, 0),
        )
        cita.actualizarEstadoPorFecha()
        self.assertEqual(cita.estado, 'ausente')

        cita = Cita.objects.create(
            paciente=paciente,
            punto_vacunacion=punto,
            vacuna=vacuna,
            fecha=date.today(),
            hora=time(8, 0),
        )
        cita.completarCita()
        self.assertEqual(cita.estado, 'completada')

    def test_vacunacion_solo_muestra_citas_agendadas_y_prioriza_la_cita(self):
        paciente = Paciente.objects.create(
            usuario=Usuario.objects.create_user(username='paciente_vacunacion', password='12345678', rol='paciente', rut='66666666-6'),
            rut='66666666-6',
            nombre='Paciente Vacunacion',
            fechaNacimiento=date(1991, 1, 1),
        )
        punto = PuntoVacunacion.objects.create(nombre='Centro', direccion='Dirección 1')
        vacuna = Vacuna.objects.create(nombre='Papiloma')
        cita_agendada = Cita.objects.create(
            paciente=paciente,
            punto_vacunacion=punto,
            vacuna=vacuna,
            fecha=date.today(),
            hora=time(12, 0),
            estado='agendada',
        )
        cita_cancelada = Cita.objects.create(
            paciente=paciente,
            punto_vacunacion=punto,
            vacuna=vacuna,
            fecha=date.today(),
            hora=time(13, 0),
            estado='cancelada',
        )

        form = VacunacionForm()

        self.assertEqual(list(form.fields.keys())[:2], ['cita', 'paciente'])
        self.assertEqual(list(form.fields['cita'].queryset), [cita_agendada])

    @patch('vacunacion.views.enviar_correo_resend')
    def test_agendar_cita_envia_correo_de_confirmacion(self, enviar_correo):
        paciente = Paciente.objects.create(
            usuario=Usuario.objects.create_user(username='paciente_correo', password='12345678', rol='paciente', rut='12121212-1', email='paciente@example.com'),
            rut='12121212-1',
            nombre='Paciente Correo',
            fechaNacimiento=date(1990, 1, 1),
        )
        punto = PuntoVacunacion.objects.create(nombre='Centro', direccion='Dirección 1')
        vacuna = Vacuna.objects.create(nombre='Covid-19')
        Stock.objects.create(vacuna=vacuna, punto_vacunacion=punto, cantidad=3)

        self.client.force_login(paciente.usuario)
        response = self.client.post(reverse('agendar_cita'), {
            'punto_vacunacion': punto.idPunto,
            'vacuna': vacuna.idTipo,
            'correo': 'paciente@example.com',
            'fecha': date.today().isoformat(),
            'hora': '10:00',
        })

        self.assertEqual(response.status_code, 302)
        cita = Cita.objects.get(paciente=paciente)
        self.assertEqual(cita.correo, 'paciente@example.com')
        enviar_correo.assert_called_once()

    @patch('vacunacion.views.enviar_correo_resend')
    def test_registrar_vacunacion_envia_correo_de_confirmacion(self, enviar_correo):
        paciente = Paciente.objects.create(
            usuario=Usuario.objects.create_user(username='paciente_vacunacion_correo', password='12345678', rol='paciente', rut='13131313-1', email='paciente2@example.com'),
            rut='13131313-1',
            nombre='Paciente Vacunacion',
            fechaNacimiento=date(1990, 1, 1),
        )
        punto = PuntoVacunacion.objects.create(nombre='Centro', direccion='Dirección 2')
        vacuna = Vacuna.objects.create(nombre='Influenza')
        cita = Cita.objects.create(
            paciente=paciente,
            punto_vacunacion=punto,
            vacuna=vacuna,
            fecha=date.today(),
            hora=time(9, 0),
            correo='paciente2@example.com',
            estado='agendada',
        )
        personal = PersonalSalud.objects.create(
            usuario=Usuario.objects.create_user(username='salud_correo', password='12345678', rol='personal_salud', rut='14141414-1'),
            rut='14141414-1',
            nombre='Personal Salud',
            rol='Enfermero',
        )
        Stock.objects.create(vacuna=vacuna, punto_vacunacion=punto, cantidad=5)

        self.client.force_login(personal.usuario)
        response = self.client.post(reverse('registrar_vacunacion'), {
            'cita': cita.idCita,
            'paciente': paciente.pk,
            'vacuna': vacuna.idTipo,
            'fecha': date.today().isoformat(),
            'hora': '09:30',
        })

        self.assertEqual(response.status_code, 302)
        enviar_correo.assert_called_once()

    def test_enviar_recordatorios_citas(self):
        paciente = Paciente.objects.create(
            usuario=Usuario.objects.create_user(username='paciente_recordatorio', password='12345678', rol='paciente', rut='15151515-1', email='recordatorio@example.com'),
            rut='15151515-1',
            nombre='Paciente Recordatorio',
            fechaNacimiento=date(1990, 1, 1),
        )
        punto = PuntoVacunacion.objects.create(nombre='Centro', direccion='Dirección 3')
        vacuna = Vacuna.objects.create(nombre='Hepatitis B')
        cita = Cita.objects.create(
            paciente=paciente,
            punto_vacunacion=punto,
            vacuna=vacuna,
            fecha=date.today() + timedelta(days=1),
            hora=time(9, 0),
            correo='recordatorio@example.com',
            estado='agendada',
        )

        with patch('vacunacion.views.enviar_correo_resend', return_value=True) as enviar_correo:
            enviar_recordatorios_citas()

        cita.refresh_from_db()
        self.assertTrue(cita.recordatorio_enviado)
        enviar_correo.assert_called_once()

    def test_dashboard_paciente_solo_muestra_citas_agendadas(self):
        paciente = Paciente.objects.create(
            usuario=Usuario.objects.create_user(username='paciente_dashboard', password='12345678', rol='paciente', rut='77777777-7'),
            rut='77777777-7',
            nombre='Paciente Dashboard',
            fechaNacimiento=date(1990, 1, 1),
        )
        punto = PuntoVacunacion.objects.create(nombre='Centro', direccion='Dirección 1')
        vacuna = Vacuna.objects.create(nombre='Hepatitis B')
        cita_agendada = Cita.objects.create(
            paciente=paciente,
            punto_vacunacion=punto,
            vacuna=vacuna,
            fecha=date.today(),
            hora=time(9, 0),
            estado='agendada',
        )
        Cita.objects.create(
            paciente=paciente,
            punto_vacunacion=punto,
            vacuna=vacuna,
            fecha=date.today(),
            hora=time(10, 0),
            estado='cancelada',
        )

        self.client.force_login(paciente.usuario)
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['citas']), [cita_agendada])

    def test_registrar_vacunacion_autocompleta_paciente_y_vacuna_desde_la_cita(self):
        paciente = Paciente.objects.create(
            usuario=Usuario.objects.create_user(username='paciente_autocompletar', password='12345678', rol='paciente', rut='88888888-8'),
            rut='88888888-8',
            nombre='Paciente Autocompletar',
            fechaNacimiento=date(1991, 2, 2),
        )
        punto = PuntoVacunacion.objects.create(nombre='Centro', direccion='Dirección 2')
        vacuna = Vacuna.objects.create(nombre='Influenza')
        cita = Cita.objects.create(
            paciente=paciente,
            punto_vacunacion=punto,
            vacuna=vacuna,
            fecha=date.today(),
            hora=time(11, 0),
            estado='agendada',
        )

        personal = PersonalSalud.objects.create(
            usuario=Usuario.objects.create_user(username='salud_autocompletar', password='12345678', rol='personal_salud', rut='99999999-9'),
            rut='99999999-9',
            nombre='Personal Salud',
            rol='Enfermero',
        )
        self.client.force_login(personal.usuario)

        response = self.client.get(reverse('registrar_vacunacion'), {'cita': cita.idCita})

        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertEqual(form.fields['paciente'].initial, paciente.pk)
        self.assertEqual(form.fields['vacuna'].initial, vacuna.pk)

    def test_crear_campana_muestra_campo_de_vacuna(self):
        self.client.force_login(self.usuario)
        response = self.client.get(reverse('crear_campana'))
        self.assertContains(response, 'Vacuna asociada')
