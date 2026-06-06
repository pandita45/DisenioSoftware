from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Paciente
    path('citas/agendar/', views.agendar_cita, name='agendar_cita'),
    path('citas/', views.mis_citas, name='mis_citas'),
    path('citas/cancelar/<int:cita_id>/', views.cancelar_cita, name='cancelar_cita'),
    path('historial/', views.mi_historial, name='mi_historial'),

    # Personal Salud
    path('vacunacion/registrar/', views.registrar_vacunacion, name='registrar_vacunacion'),
    path('pacientes/', views.lista_pacientes, name='lista_pacientes'),
    path('pacientes/registrar/', views.registrar_paciente, name='registrar_paciente'),
    path('pacientes/<int:paciente_id>/historial/', views.historial_paciente, name='historial_paciente'),

    # MINSAL
    path('campanas/', views.gestionar_campanas, name='gestionar_campanas'),
    path('campanas/crear/', views.crear_campana, name='crear_campana'),
    path('campanas/eliminar/<int:campana_id>/', views.eliminar_campana, name='eliminar_campana'),
    path('reporte/', views.reporte_vacunaciones, name='reporte_vacunaciones'),

    # API
    path('api/stock/', views.verificar_stock_ajax, name='verificar_stock'),
]
