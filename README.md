# DisenioSoftware
# VacunaChile — Sistema de Vacunación MINSAL

## Requisitos previos

Tener instalado **Python 3.10 o superior**.

## Instalación paso a paso

### 1. Abrir terminal en la carpeta del proyecto
Luego navegar a la carpeta correcta:
```bash
cd implementacion_del_sistema/implementacion_del_sistema/vacunas_minsal
```

### 3. Crear el entorno virtual
```bash
python -m venv venv
```

### 4. Activar el entorno virtual
En Windows:
```bash
venv\Scripts\activate
```
En Mac/Linux:
```bash
source venv/bin/activate
```

Si en Windows aparece un error de permisos, ejecutar primero:
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Y luego volver a activar (4).

Cuando el entorno esté activo, vera **(venv)** al inicio de la línea.

### 5. Instalar Django y dependencias
```bash
pip install -r requirements.txt
```

### 6. Iniciar el servidor
```bash
python manage.py runserver
```

### 7. Abrir en el navegador
Se copia la url entregada en la terminar y se pega en el navegador que usa


