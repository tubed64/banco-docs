# Aplicación Bancaria de Validación de Documentos

Aplicación web en Python/Django para que clientes suban documentos (PDF o imágenes) y los trabajadores los validen o soliciten correcciones.

## Características

- Registro y autenticación de usuarios.
- Roles: cliente y trabajador.
- Subida de documentos como PDF o imagen.
- Panel de trabajadores para validar documentos.
- Flujo de rechazo con comentario y corrección.

## Requisitos

- Python 3.11+ recomendado.
- Django 4.2+

## Instalación

1. Crear un entorno virtual:

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

3. Ejecutar migraciones:

```bash
python manage.py migrate
```

4. Crear superusuario:

```bash
python manage.py createsuperuser
```

5. Ejecutar servidor:

```bash
python manage.py runserver
```

## Uso

- Clientes: crear cuenta e iniciar sesión para subir documentos desde la página principal.
- Trabajadores: configurar usuarios como trabajadores desde el admin y revisar documentos en el panel para aprobar o rechazar.
- El detalle del documento muestra historial de cambios y rechazos.

## Ver la aplicación

1. Inicia el servidor con `python manage.py runserver`.
2. Abre en el navegador: `http://127.0.0.1:8000/`.
3. Usa `http://127.0.0.1:8000/register/` para crear una cuenta de cliente.
4. Accede al panel de administración en `http://127.0.0.1:8000/dashboard-admin/` para gestionar validadores.

## Base de datos y scripts SQL

- La base de datos de desarrollo es `db.sqlite3`.
- El proyecto ahora carga la configuración de base de datos desde `.env`.
- Se incluye el directorio `sql_scripts/` con un ejemplo de esquema para SQL Server:
  - `sql_server_schema.sql`
  - `README.md`
- El script SQL Server incluye:
  - Tablas de auditoría y triggers para los cambios en documentos y comentarios.
  - Índices para consultas rápidas por usuario, estado y trabajador asignado.
  - Procedimientos almacenados con `TRY/CATCH` para insertar documentos, comentarios y historial.
  - Procedimientos para obtener documentos pendientes y rechazados.

## Notas

- Para crear trabajadores, ingresa al admin de Django y marca `is_worker` en el perfil del usuario.
- El proyecto está construido para funcionar con migraciones de Django; si usas SQL Server, el script `sql_scripts/sql_server_schema.sql` es una referencia para el esquema.
- Modifica `.env` si deseas conectar otro motor de base de datos.
