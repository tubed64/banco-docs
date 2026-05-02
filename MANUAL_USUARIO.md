# 📖 Manual de Usuario - Sistema de Validación Bancaria

> **Versión 2.0** | Última actualización: Abril 2026

---

## 🎯 Contenido

- [Introducción](#introducción)
- [Características Principales](#características-principales)
- [Acceso al Sistema](#acceso-al-sistema)
- [Guía para Clientes](#guía-para-clientes)
- [Guía para Validadores Nivel 1](#guía-para-validadores-nivel-1)
- [Guía para Validadores Nivel 2](#guía-para-validadores-nivel-2)
- [Guía para Administradores](#guía-para-administradores)
- [Preguntas Frecuentes](#preguntas-frecuentes)
- [Soporte Técnico](#soporte-técnico)

---

## 📋 Introducción

Bienvenido al **Sistema de Validación de Documentos Bancarios**. Esta plataforma automatiza y agiliza el proceso de validación de documentos para solicitudes de crédito mediante:

- **Inteligencia Artificial (IA)** para extracción automática de datos
- **Validación de 2 niveles** para máxima precisión
- **Cifrado de datos** para seguridad PII (información personal)
- **Auditoría completa** de todas las operaciones

### ¿Para qué sirve?

Esta plataforma facilita:
1. ✅ Validación rápida de documentos bancarios
2. ✅ Extracción automática de CURP, RFC, dirección, teléfono, etc.
3. ✅ Revisión por dos validadores independientes
4. ✅ Exportación automática a sistema ERP
5. ✅ Notificaciones por correo electrónico

---

## 🚀 Características Principales

### Extracción Inteligente de Datos (IA)

La plataforma utiliza **OCR avanzado + IA** para extraer automáticamente:

| Campo | Precisión | Formato |
|-------|-----------|---------|
| **CURP** | 100% | 18 caracteres (ej: PEGJ850415HDFNRN09) |
| **RFC** | 100% | 12-13 caracteres (ej: PEGJ850415FG9) |
| **Nombres** | 95%+ | Nombre completo del solicitante |
| **Teléfono** | 95%+ | Múltiples formatos mexicanos |
| **Email** | 100% | Dirección de correo válida |
| **Dirección** | 90%+ | Calle, número, apartado, etc. |
| **Ocupación** | 90%+ | Profesión o actividad |
| **Estado Civil** | 95%+ | Soltero, Casado, Divorciado, etc. |
| **Fechas** | 100% | Formato DD/MM/YYYY |

### Validación en 2 Niveles

```
┌─────────────────────────────────────────────┐
│ 1. CLIENTE SUBE DOCUMENTO                   │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│ 2. IA EXTRAE DATOS & VALIDA                 │
│    (CURP, RFC, Consistencia)                │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│ 3. VALIDADOR NIVEL 1 REVISA                 │
│    (Revisión de IA + Decisión)              │
└──────────────────┬──────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
    ✗ RECHAZA            ✓ APRUEBA
        │                     │
        │        ┌────────────▼─────────────┐
        │        │ 4. VALIDADOR NIVEL 2    │
        │        │    CONFIRMACIÓN FINAL    │
        │        └────────────┬─────────────┘
        │                     │
        │        ┌────────────┴──────────┐
        │        │                       │
        │    ✗ RECHAZA             ✓ APRUEBA
        │        │                       │
        │        │        ┌──────────────▼────┐
        │        │        │ 5. EXPORTAR A ERP │
        │        │        └───────────────────┘
        │        │
    ┌───▼────────▼────┐
    │ CLIENTE          │
    │ NOTIFICADO       │
    └──────────────────┘
```

### Seguridad de Datos

- 🔐 **Encriptación Fernet** para campos sensibles (CURP, RFC, teléfono, etc.)
- 🛡️ **Autenticación Django** con control de acceso por rol
- 📋 **Auditoría completa** de todas las acciones
- 🔒 **Tokens CSRF** en todos los formularios

---

## 🔑 Acceso al Sistema

### URL de Acceso

```
http://localhost:8000/
```

### Tipos de Usuarios

| Rol | Usuario | Contraseña | Dashboard |
|-----|---------|-----------|-----------|
| **Admin** | diego | diego123 | /dashboard-admin/ |
| **Validador 1** | validador1 | validate123 | /validator1/ |
| **Validador 2** | validador2 | validate123 | /validator2/ |
| **Cliente** | (Auto-registrado) | (Personal) | /home/ |

---

## 👥 Guía para Clientes

### 1. Registrarse en el Sistema

**Paso 1:** Accede a la página principal
- URL: `http://localhost:8000/`
- Haz clic en **"Registrarse"**

**Paso 2:** Completa el formulario
```
Nombre:           [Tu nombre completo]
Nombre de usuario: [nombre_usuario]
Email:            [tu@email.com]
Contraseña:       [mínimo 8 caracteres]
Repetir contraseña:[confirma]
```

**Paso 3:** Haz clic en **"Crear Cuenta"**

✅ Tu cuenta está lista. Recibirás confirmación por correo.

### 2. Subir Documento para Validación

**Paso 1:** Inicia sesión
- Username: [tu usuario]
- Password: [tu contraseña]

**Paso 2:** Accede a /home/
- Verás el formulario **"Solicitar Validación de Documento"**

**Paso 3:** Completa el formulario

```
Tipo de Crédito:*
  ☐ Crédito Personal
  ☐ Hipotecario
  ☐ Automotriz
  ☐ Comercial

Documento Scaneado:* (PDF, JPG, PNG - Máx 5MB)
  [Seleccionar archivo...]

INE/Identificación: (Opcional)
  [Seleccionar archivo...]

Pasaporte: (Opcional)
  [Seleccionar archivo...]

CURP (si está disponible):
  [18 caracteres, ej: PEGJ850415HDFNRN09]

RFC (si está disponible):
  [12-13 caracteres, ej: PEGJ850415FG9]
```

**Paso 4:** Haz clic en **"Subir Documento"**

✅ Tu documento ha sido enviado. Te notificaremos por correo cuando se complete la validación.

### 3. Monitorear Estado de Solicitud

**Opción A - Via Panel**
1. Inicia sesión
2. Ve a /home/
3. En la sección **"Mis Documentos"**, verás:
   - ⏳ **Pendiente** - En cola de validación
   - 👁️ **Revisión** - Siendo validado
   - ✅ **Aprobado** - Listo para ERP
   - ❌ **Rechazado** - Requiere correcciones

**Opción B - Via Email**
- Recibirás correos automáticos en cada etapa:
  - "Documento recibido"
  - "En proceso de validación"
  - "Aprobado / Rechazado"

### 4. Si tu Documento fue Rechazado

**Razones comunes de rechazo:**

1. **"Documento ilegible o borroso"**
   - ✓ Sube una copia más clara
   - ✓ Asegúrate de que el texto sea legible
   - ✓ Usa escáner en lugar de fotografía si es posible

2. **"Datos no coinciden entre documentos"**
   - ✓ Verifica que CURP, RFC y nombre coincidan
   - ✓ Compara los valores en INE y documento comprobante
   - ✓ Reenvía con documentos actualizados

3. **"Información incompleta"**
   - ✓ Completa todos los campos requeridos
   - ✓ Incluye el CURP y RFC si está disponible

**Para reenviar:**
1. Revisa el motivo del rechazo en el correo
2. Realiza las correcciones necesarias
3. Vuelve a subir el documento mejorado
4. El proceso se reinicia automáticamente

---

## 👨‍💼 Guía para Validadores Nivel 1

### Rol y Responsabilidades

- ✓ Revisar documentos en la **primera etapa**
- ✓ Verificar que datos extraídos sean correctos
- ✓ Validar CURP y RFC automáticamente
- ✓ **Aprobar o Rechazar** con justificación
- ✓ Enviar documentos a Validador Nivel 2 (si aprueba)

### 1. Acceder al Panel

**URL:** `http://localhost:8000/validator1/`

**Credenciales de prueba:**
```
Usuario: validador1
Contraseña: validate123
```

**Dashboard Validador 1:**

```
┌─────────────────────────────────────────┐
│ 📋 VALIDADOR NIVEL 1                    │
│                                         │
│ 📊 Estadísticas:                        │
│   ⏳ Pendientes: 5                      │
│   👁️ Bajo revisión: 3                   │
│   ✅ Aprobados: 42                      │
│   ❌ Rechazados: 8                      │
│                                         │
│ 📝 Mis Documentos en Revisión:          │
│   [1] Documento #0025 - Juan Pérez     │
│   [2] Documento #0026 - María García    │
│   [3] Documento #0027 - Carlos López    │
└─────────────────────────────────────────┘
```

### 2. Revisar un Documento

**Paso 1:** Haz clic en el documento a revisar

**Paso 2:** Verás la pantalla de revisión con:

```
┌─────────────────────────────────────────────────────┐
│ 🤖 ANÁLISIS AUTOMÁTICO INTELIGENTE                  │
│                                                     │
│ Puntuación General: ████████░ 85%                  │
│                                                     │
│ ✅ PUEDE APROBARSE AUTOMÁTICAMENTE                  │
│                                                     │
│ Validaciones:                                       │
│  ✅ CURP: Válido (PEGJ850415HDFNRN09)             │
│  ✅ RFC: Válido (PEGJ850415FG9)                    │
│  ✅ Consistencia: Datos coinciden                   │
│                                                     │
│ Confianza OCR: 92%                                  │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ 📊 DATOS EXTRAÍDOS POR IA                           │
│                                                     │
│ 🆔 CURP: PEGJ850415HDFNRN09                        │
│ 🏛️ RFC: PEGJ850415FG9                              │
│ 👤 Nombres: Juan Carlos Pérez García               │
│ 📞 Teléfono: 55-2345-6789                          │
│ 📧 Email: juan.perez@email.com                     │
│ 🏘️ Dirección: Avenida Paseo de la Reforma 505...  │
│ 💼 Ocupación: Ingeniero                            │
│ 💑 Estado Civil: Casado                            │
│ 📅 Fechas: 15/04/2025                              │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ 📄 INFORMACIÓN DEL DOCUMENTO                        │
│                                                     │
│ Cliente: Juan Carlos Pérez García                   │
│ Tipo: Crédito Personal                              │
│ CURP: PEGJ850415HDFNRN09                           │
│ RFC: PEGJ850415FG9                                 │
│ Teléfono: 55-2345-6789                             │
│ Domicilio: Avenida Paseo de la Reforma...          │
│ Estado: Ciudad de México                            │
└─────────────────────────────────────────────────────┘
```

**Paso 3:** Añade comentarios (opcional)

```
Comentarios:
[Caja de texto para tus notas]
```

**Paso 4:** Toma una decisión

### 3. Aprobar Documento

**Paso 1:** Haz clic en **"✓ Aprobar Documento"**

**Paso 2:** Confirma en el modal

```
╔════════════════════════════════════════╗
║ ✓ Confirmar Aprobación                ║
╠════════════════════════════════════════╣
║                                        ║
║ ¿Estás seguro de que deseas aprobar    ║
║ este documento?                        ║
║                                        ║
║ Puntuación IA: 85%                     ║
║ Recomendación: APROBACIÓN AUTOMÁTICA   ║
║ CURP Válido: ✅                        ║
║ RFC Válido: ✅                         ║
║ Datos Consistentes: ✅                 ║
║                                        ║
║ [✓ Confirmar]  [Cancelar]              ║
╚════════════════════════════════════════╝
```

**Paso 3:** El documento se envía automáticamente a Validador Nivel 2

✅ **Resultado:**
- Documento en estado "Pendiente Validador 2"
- Cliente recibe correo informativo
- Validador 2 lo recibe en su cola

### 4. Rechazar Documento

**Paso 1:** Haz clic en **"✗ Rechazar Documento"**

**Paso 2:** Selecciona un motivo

```
☐ Documento ilegible o borroso
☐ Datos no coinciden entre documentos
☐ CURP o RFC inválido
☐ Información incompleta
☐ Sospecha de fraude
☐ Otro (especificar)
```

**Paso 3:** Escribe detalles (obligatorio)

```
Detalles del Rechazo:
[Explica por qué se rechaza, qué debe corregir el cliente]
```

**Paso 4:** Confirma

```
╔════════════════════════════════════════╗
║ ✗ Confirmar Rechazo                    ║
╠════════════════════════════════════════╣
║                                        ║
║ Se enviará correo al cliente con los   ║
║ motivos del rechazo.                   ║
║                                        ║
║ [✓ Confirmar Rechazo]  [Cancelar]      ║
╚════════════════════════════════════════╝
```

✅ **Resultado:**
- Documento en estado "Rechazado"
- Cliente recibe correo con motivos
- Cliente puede reenviar documento mejorado

### 5. Atajos de Teclado

```
ESC         → Cerrar modal de confirmación
Enter       → Confirmar decisión
Tab         → Navegar entre campos
```

---

## 👨‍⚖️ Guía para Validadores Nivel 2

### Rol y Responsabilidades

- ✓ Revisar decisión de Validador Nivel 1
- ✓ Realizar **validación final** del documento
- ✓ **Confirmar o Rechazar** la aprobación
- ✓ Si aprueba: documento se exporta a **ERP automáticamente**

### 1. Acceder al Panel

**URL:** `http://localhost:8000/validator2/`

**Credenciales de prueba:**
```
Usuario: validador2
Contraseña: validate123
```

### 2. Dashboard Validador 2

```
┌─────────────────────────────────────────┐
│ ✓ VALIDADOR NIVEL 2 (CONFIRMACIÓN)      │
│                                         │
│ 📊 Estadísticas:                        │
│   ⏳ Pendientes: 2                      │
│   👁️ Bajo revisión: 1                   │
│   ✅ Aprobados: 38                      │
│   ❌ Rechazados: 5                      │
│                                         │
│ 📝 Documentos Pendientes de Confirmación│
│   [1] Documento #0024 - Roberto Martín  │
│   [2] Documento #0025 - Ana López       │
└─────────────────────────────────────────┘
```

### 3. Revisar Documento

**Paso 1:** Haz clic en el documento

**Paso 2:** Verás la pantalla con:

```
┌─────────────────────────────────────────────────────┐
│ 📋 REVISIÓN DE VALIDADOR 1                          │
│                                                     │
│ Decisión: ✅ APROBADO                               │
│ Validador: validador1 (Juan García)                │
│ Fecha: 2026-04-28 10:35                            │
│ Comentarios: Documento correcto, CURP y RFC válidos│
│                                                     │
│ [Mostrar más detalles ▼]                            │
└─────────────────────────────────────────────────────┘

[Misma sección de datos extraídos y análisis IA]
```

### 4. Confirmar (Aprobar Final)

**Paso 1:** Haz clic en **"✓ Aprobar Documento"**

**Paso 2:** Confirma en el modal

```
╔════════════════════════════════════════╗
║ ✓ Confirmar Aprobación Final           ║
╠════════════════════════════════════════╣
║                                        ║
║ Esta es la APROBACIÓN FINAL.           ║
║ El documento será exportado a ERP.     ║
║                                        ║
║ Cliente: Juan Pérez (juan.perez@...)   ║
║ Tipo: Crédito Personal                 ║
║ Estado: APROBACIÓN FINAL                ║
║                                        ║
║ [✓ Confirmar]  [Cancelar]              ║
╚════════════════════════════════════════╝
```

**Paso 3:** Listo ✅

- Documento en estado "Aprobado"
- Automáticamente se exporta a ERP
- Cliente recibe correo de aprobación
- Solicitud lista para procesamiento de crédito

### 5. Rechazar (Segunda Instancia)

**Paso 1:** Haz clic en **"✗ Rechazar Documento"**

**Paso 2:** Sigue el mismo proceso que Validador 1

- Selecciona motivo
- Añade detalles
- Confirma

**Nota:** El rechazo en Nivel 2 es **final**. El cliente deberá contactar con administración.

---

## 🔐 Guía para Administradores

### Rol y Responsabilidades

- ✓ Gestionar usuarios validadores
- ✓ Monitorear auditoría de operaciones
- ✓ Crear, editar, eliminar validadores
- ✓ Ver logs de todas las acciones del sistema
- ✓ Resolver escalamientos

### 1. Acceder al Panel Admin

**URL:** `http://localhost:8000/dashboard-admin/`

**Credenciales de prueba:**
```
Usuario: diego
Contraseña: diego123
```

### 2. Panel de Control Admin

```
┌───────────────────────────────────────────────────┐
│ 🔐 PANEL DE ADMINISTRACIÓN                        │
│                                                   │
│ 📊 Dashboard:                                     │
│   👥 Total Usuarios: 156                          │
│   📄 Documentos Pendientes: 8                     │
│   ✅ Documentos Aprobados (Hoy): 12              │
│   ❌ Documentos Rechazados (Hoy): 2              │
│   👨‍💼 Validadores Activos: 8                      │
│                                                   │
│ 🔧 OPCIONES:                                      │
│   [1] Gestionar Validadores                       │
│   [2] Ver Registro de Auditoría                   │
│   [3] Monitor de Sistema                          │
│   [4] Configuración                               │
└───────────────────────────────────────────────────┘
```

### 3. Gestionar Validadores

#### Crear Nuevo Validador

**Paso 1:** Haz clic en **"[+] Crear Validador"**

**Paso 2:** Completa el formulario

```
Información Personal:
├─ Nombre:*           [Juan García]
├─ Apellido:*         [López]
├─ Email:*            [juan.garcia@banco.com]

Credenciales:
├─ Usuario:*          [jgarcia_val1]
├─ Contraseña:*       [GenerateSecure123!]
├─ Nivel:*            ☐ Validador 1  ☐ Validador 2

Estado:
└─ Activo:            ☑️ Sí
```

**Paso 3:** Haz clic en **"[✓ Crear Validador]"**

✅ **Resultado:**
- Nueva cuenta creada
- Email de bienvenida enviado
- Validador puede acceder con credenciales

#### Editar Validador

**Paso 1:** Ve a **"Gestionar Validadores"**

**Paso 2:** Haz clic en el botón **"[✏️ Editar]"** del validador

**Paso 3:** Modifica los campos necesarios

```
Opciones para editar:
├─ Nombre / Apellido
├─ Email
├─ Nivel de Validación
├─ Estado (Activo/Inactivo)
└─ Cambiar Contraseña
```

**Paso 4:** Haz clic en **"[✓ Guardar Cambios]"**

#### Desactivar Validador

**Método 1 - Desactivación Temporal:**
1. Haz clic en **"[✏️ Editar]"**
2. Marca como **"Inactivo"**
3. El usuario no podrá acceder

**Método 2 - Eliminar:**
1. Haz clic en **"[🗑️ Eliminar]"**
2. Confirma la acción
3. El validador se elimina del sistema

### 4. Monitor de Auditoría

**URL:** `http://localhost:8000/dashboard-admin/audit-log/`

```
┌────────────────────────────────────────────────────┐
│ 📋 REGISTRO DE AUDITORÍA                           │
│                                                    │
│ Filtros:                                           │
│  ├─ Acción: [Seleccionar...]                      │
│  ├─ Usuario: [Seleccionar...]                     │
│  └─ Tabla: [Seleccionar...]                       │
│                                                    │
│ Registro (Últimas operaciones):                    │
│                                                    │
│ 2026-04-28 14:32 | validador1 | document | INSERT │
│   → Documento #0028 subido                         │
│                                                    │
│ 2026-04-28 14:15 | validador1 | document | UPDATE │
│   → Documento #0027 aprobado (Nivel 1)            │
│                                                    │
│ 2026-04-28 13:45 | diego | document | UPDATE      │
│   → Validador asignado al documento #0026        │
│                                                    │
│ [◄ Anterior] [1 2 3 4 5] [Siguiente ►]             │
└────────────────────────────────────────────────────┘
```

**Campos de auditoría:**
- **Timestamp:** Fecha y hora exacta
- **Usuario:** Quién realizó la acción
- **Tabla:** Qué se modificó
- **Acción:** INSERT/UPDATE/DELETE
- **Detalles:** Qué cambió específicamente

---

## ❓ Preguntas Frecuentes

### 🔐 Seguridad

**P: ¿Mis datos son seguros?**
R: Sí. Usamos encriptación Fernet para datos sensibles (CURP, RFC, teléfono). Además:
   - Autenticación Django robusta
   - Control de acceso por rol
   - HTTPS en producción
   - Auditoría de todas las operaciones

**P: ¿Quién puede ver mis datos?**
R: Solo el cliente y los 2 validadores asignados. Cada validador solo ve lo que necesita.

**P: ¿Se borra mi información después?**
R: Los datos se mantienen en el sistema por requisitos de auditoría bancaria. Se cifran de forma segura.

### 📤 Subir Documentos

**P: ¿Qué formatos acepta?**
R: JPG, PNG, PDF (máximo 5MB). Recomendamos:
   - JPG para fotos
   - PDF para documentos escaneados
   - Resolución mínima 300 DPI

**P: ¿Puedo subir un documento de nuevo?**
R: Si fue rechazado, sí. Solo haz click en "Reenviar" desde tu panel.

**P: ¿Cuánto tarda la validación?**
R: Normalmente 24-48 horas. El análisis IA es instantáneo, pero requiere revisión manual.

### ✅/❌ Validación

**P: ¿Por qué fue rechazado mi documento?**
R: Revisa el correo de rechazo. Razones comunes:
   - Documento ilegible
   - Datos inconsistentes
   - CURP/RFC inválido
   - Información incompleta

**P: ¿Puedo apelar un rechazo?**
R: Sí. Contacta con administración con detalles del documento. Se revisará nuevamente.

**P: ¿Qué es la "Puntuación IA"?**
R: Es un indicador 0-100% de confianza en los datos extraídos:
   - 85-100%: Muy confiable
   - 60-84%: Revisar cuidadosamente
   - <60%: Se recomienda rechazar

### 📧 Correos

**P: ¿Por qué no recibo correos?**
R: 
   1. Revisa carpeta de SPAM
   2. Verifica que el email sea correcto en tu perfil
   3. Contacta con soporte

**P: ¿Puedo cambiar mi correo?**
R: Ve a tu perfil > Configuración > Cambiar Email

### 🆔 CURP y RFC

**P: ¿Cómo se valida el CURP?**
R: Se usa el algoritmo oficial de Segob (Secretaría de Gobernación). Valida:
   - Formato correcto (18 caracteres)
   - Dígito verificador válido
   - Datos coherentes (fecha de nacimiento)

**P: ¿Y si mi CURP es antiguo?**
R: Si está registrado en Segob, es válido. La IA debe extraerlo correctamente.

---

## 💬 Soporte Técnico

### Reportar un Problema

**Paso 1:** Reúne información
- Navegador y versión
- Sistema operativo
- Paso donde ocurrió el error
- Mensaje de error (si aplica)

**Paso 2:** Envía ticket a:
```
Email: soporte@banco-validacion.com
Asunto: [URGENCIA] Descripción breve
```

**Paso 3:** Describe el problema
```
Navegador: Chrome 125.0
SO: Windows 10
Error: "No se puede subir documento"
Mensaje: "File size exceeds 5MB"
Pasos para reproducir:
1. Click en "Subir documento"
2. Selecciono archivo > 5MB
3. Hago click en "Subir"
4. Error X aparece
```

### Horarios de Soporte

- **Lunes a Viernes:** 08:00 - 18:00 hrs
- **Sábados:** 09:00 - 14:00 hrs
- **Domingos/Festivos:** Cerrado (Emergencias: +52 55-1234-5678)

### Problemas Comunes y Soluciones

#### "Error: No se puede acceder al sistema"

**Solución:**
1. Limpia caché del navegador (Ctrl+Shift+Del)
2. Intenta en navegador incógnito
3. Verifica conexión a internet
4. Intenta con otro navegador

#### "Error: Documento no se carga"

**Solución:**
1. Verifica tamaño < 5MB
2. Comprueba formato (JPG, PNG, PDF)
3. Descarga el archivo e intenta de nuevo
4. Prueba en diferente navegador

#### "Error: Validación lenta"

**Solución:**
1. Es normal: OCR + IA tarda 30-60 segundos
2. No recargues la página durante el proceso
3. Si tarda >2 minutos, contacta soporte

---

## 📚 Anexos

### Glosario

| Término | Significado |
|---------|-------------|
| **CURP** | Clave Única de Registro de Población (18 caracteres) |
| **RFC** | Registro Federal de Contribuyentes (12-13 caracteres) |
| **OCR** | Optical Character Recognition (lectura de imágenes) |
| **IA** | Inteligencia Artificial (análisis automático) |
| **ERP** | Sistema de Planificación de Recursos Empresariales |
| **Rol** | Tipo de usuario (Admin, Validador 1, Validador 2, Cliente) |
| **Auditoría** | Registro de todas las acciones en el sistema |

### Atajos de Teclado

| Atajo | Función |
|-------|---------|
| `ESC` | Cerrar diálogos/modales |
| `Enter` | Confirmar decisión/formulario |
| `Tab` | Navegar entre campos |
| `Ctrl+S` | Guardar cambios |

### Contactos Importantes

```
📞 Centro de Soporte: +52 55-XXXX-XXXX
📧 Email Técnico: soporte@banco-validacion.com
📧 Email Facturación: facturación@banco-validacion.com
🏢 Oficina: Calle Principal 123, CDMX 06500
```

---

## ✍️ Historial de Cambios

| Versión | Fecha | Cambios |
|---------|-------|---------|
| 2.0 | 2026-04-28 | Integración de extracción IA mejorada, nuevo manual |
| 1.5 | 2026-03-15 | Añadida funcionalidad de dos validadores |
| 1.0 | 2026-01-01 | Lanzamiento inicial |

---

**📋 Fin del Manual de Usuario**

> Para más información, visita: `http://localhost:8000/ayuda/`
> 
> Última actualización: Abril 2026
> 
> Versión del Sistema: 2.0 | Python 3.13 | Django 6.0.3

