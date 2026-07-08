# VacunaChile — Sistema de Vacunación MINSAL

Sistema web Django para gestión de campañas de vacunación nacional, 
basado en el diagrama de clases UML del MINSAL.

## Estructura del Proyecto

```
vacunas_minsal/
├── manage.py
├── requirements.txt
├── vacunas_minsal/          # Configuración Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── vacunacion/              # App principal
    ├── models.py            # Modelos según diagrama UML
    ├── views.py             # Vistas con control de roles
    ├── forms.py             # Formularios
    ├── urls.py              # URLs
    ├── admin.py             # Panel de administración
    ├── management/
    │   └── commands/
    │       └── seed_data.py # Datos de prueba
    └── templates/
        └── vacunacion/
            ├── base.html
            ├── login.html
            ├── dashboard_paciente.html
            ├── dashboard_personal.html
            ├── dashboard_minsal.html
            ├── agendar_cita.html
            ├── mis_citas.html
            ├── historial.html
            ├── lista_pacientes.html
            ├── registrar_vacunacion.html
            ├── registrar_paciente.html
            ├── campanas.html
            ├── crear_campana.html
            └── reporte.html
```

## Instalación y Configuración

### 1. Crear entorno virtual
```bash
cd vacunas_minsal
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Aplicar migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Cargar datos de prueba
```bash
python manage.py seed_data
```

### 5. Crear superusuario (opcional, para panel admin)
```bash
python manage.py createsuperuser
```

### 6. Iniciar servidor
```bash
python manage.py runserver
```

Acceder en: http://127.0.0.1:8000

---

## Credenciales de Prueba

| Rol            | Usuario     | Contraseña |
|----------------|-------------|------------|
| 🏛️ MINSAL     | minsal1     | pass1234   |
| 🩺 Enfermera   | enfermera1  | pass1234   |
| 🩺 Médico      | medico1     | pass1234   |
| 👤 Paciente 1  | paciente1   | pass1234   |
| 👤 Paciente 2  | paciente2   | pass1234   |
| 👤 Paciente 3  | paciente3   | pass1234   |
| 👤 Paciente 4  | paciente4   | pass1234   |

---

## Funcionalidades por Rol

### Paciente
- Ver dashboard con citas próximas y vacunaciones recientes
- Agendar citas (con verificación de stock en tiempo real via AJAX)
- Cancelar citas
- Ver historial completo de vacunaciones

### Personal de Salud
- Ver pacientes y buscar por nombre/RUT
- Registrar nuevos pacientes con cuenta de usuario
- Registrar vacunaciones administradas
- Ver historial de cualquier paciente

### Personal MINSAL
- Gestionar campañas de vacunación (crear/eliminar)
- Asignar grupos de riesgo a campañas
- Ver reporte global de vacunaciones

---

## Seguridad Implementada

- **Autenticación**: sistema de login de Django con contraseñas hasheadas
- **Control de roles**: decorador `@rol_requerido` en todas las vistas sensibles
- **CSRF**: protección en todos los formularios
- **Separación de datos**: cada rol solo accede a sus propias vistas
- **Validación de stock**: verificación antes de crear citas
- **Validación de horarios**: sin solapamiento de citas en mismo slot

---

## Diagrama Implementado

El sistema implementa fielmente el diagrama de clases:

- `PersonalMinsal` gestiona `Campana`
- `Campana` involucra `Paciente` y se dirige a `GrupoRiesgo`
- `Paciente` pertenece a `GrupoRiesgo` y agenda `Cita`
- `Cita` se realiza en `PuntoVacunacion` y da lugar a `Vacunacion`
- `PersonalSalud` administra `Vacunacion` y registra `Paciente`
- `PuntoVacunacion` dispone de `Stock` de `Vacuna`
- `Vacunacion` está ligada a `Vacuna` y la utiliza

Los diagramas de comunicación también están implementados:
- **GestorCita**: lógica en `views.agendar_cita` (verifica stock y horario, crea Cita)
- **GestorConsultas**: lógica en `views.mi_historial` / `historial_paciente`
