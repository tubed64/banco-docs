# SQL Scripts para la base de datos

Este proyecto Django usa `db.sqlite3` como base de datos de desarrollo.

También se incluye un script de ejemplo para SQL Server con:

- Tablas: `User`, `Profile`, `Document`, `DocumentComment`, `DocumentHistory`, `AuditLog`
- Índices para mejorar consultas de estado, usuario y asignación
- Triggers de auditoría en SQL Server para capturar cambios en `Document` y `DocumentComment`
- Procedimientos almacenados con `TRY/CATCH`:
  - `usp_CreateDocument`
  - `usp_CreateDocumentComment`
  - `usp_AddDocumentHistory`
  - `usp_UpdateDocumentStatus`
  - `usp_GetPendingDocumentsByWorker`
  - `usp_GetRejectedDocuments`

## Cómo usar

1. Abre `sql_scripts/sql_server_schema.sql` con SQL Server Management Studio o Azure Data Studio.
2. Ejecuta el script para crear las tablas y los procedimientos.
3. Ajusta el esquema si usas otro motor de base de datos.

> El proyecto Django actual está configurado para SQLite y usa migraciones de Django.
