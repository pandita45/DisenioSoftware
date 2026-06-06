# Patrones de Diseño a implementar
## Singleton MINSAL y Prototype para Campañas
El MINSAL es la principal entidad reguladora y auditora de las campañas. Al implementar el patrón Singleton para su creación se garantiza una instancia única global, lo que es crucial para la seguridad de los datos, eliminando la posibilidad de duplicidad, inconsistencia o pérdida de registros.
La campañas de vacucación comparten una estructura de creación idéntica (período de campaña, grupo objetivo, tipo de vacuna, etc.), por lo que implementar el patrón Prototype simplifica la creación de nuevas campañas, partiendo desde esqueleto básico preexistente.

<img width="1562" height="738" alt="image" src="https://github.com/user-attachments/assets/e3a03ff6-53db-4c18-8b85-86f9b3842745" />

## Factory Usuarios 
Dentro del modelo de negocio se considera la existencia de entidades asociadas a personas, las cuales comparten credenciales comunes tales como el RUT o el nombre, por lo que implementar un patrón Factory desde una base común Persona, donde las entidades creadas difieran únicamente en su rol y permiso, permite disminuir el acoplamiento dentro del sistema.

<img width="2265" height="559" alt="image" src="https://github.com/user-attachments/assets/d6ce82a2-fc48-43ec-8f25-37e884a4f644" />

## Facade Vacunación
El proceso de vacunación involucra demasiadas interacciones con subsistemas del negocio, por lo que implementar un patrón Facade que simplifique la entrada de datos y luego coordine con los subsistemas es la mejor solución para facilitar esta tarea.

<img width="2408" height="462" alt="image" src="https://github.com/user-attachments/assets/d154e73e-59c7-4243-946f-f4847b82b622" />

## State Cita
Una cita pasa por diversos estados a la hora de realizar una vacunación, por lo que el patrón State permite encapsular cada uno en su propia clase, permitiendo que el objeto Cita varíe su comportamiento dinámicamente. Además, al implementar State, se facilita la auditoría de citas ya completas en caso de ser necesario. 

<img width="3019" height="757" alt="image" src="https://github.com/user-attachments/assets/8de8a6f1-0d43-454c-a707-33c0ae38bd5c" />
