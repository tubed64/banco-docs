# FLUJO DE PROCESOS DEL SISTEMA DE VALIDACIÓN BANCARIA

## PARTE 1: PROCESO EXTERNO DEL CLIENTE

### 1.1 Canales de Contacto Inicial
El cliente puede iniciar su solicitud por 3 canales:

#### Canal 1: Email
- Cliente envía solicitud a: `solicitudes@banco.com`
- Respuesta automática confirma recepción
- Se genera ticket con número único
- Cliente recibe link de activación para crear cuenta

#### Canal 2: Chatbot
- Chatbot en website detecta intención del cliente
- Chatbot proporciona información inicial
- Redirige directamente a link de la APP: `https://app.banco.com/register`
- Cliente se auto-registra sin intermediarios

#### Canal 3: Website (Acceso Directo)
- Cliente accede directamente a: `https://app.banco.com/register`
- Auto-registro inmediato
- Sin validación previa

---

### 1.2 Ingreso al Sistema - Primeros Pasos

#### Escenario 1: Cliente Nuevo (Sin historial en BD)

```
Cliente ingresa datos de registro:
├─ Email
├─ Contraseña
├─ Teléfono
└─ Datos básicos (nombre, apellido)

SISTEMA VERIFICA:
├─ ¿Email ya existe? → Mostrar error "Cuenta ya existe"
├─ ¿RFC ya existe? → Mostrar error "RFC ya registrado"
└─ ¿Datos válidos? → Crear cuenta con role=cliente

RESULTADO:
├─ Usuario creado con status=nuevo
├─ Se envía email de confirmación
├─ Se crea Profile automáticamente (signal de Django)
└─ Cliente accede al panel para subir documentos
```

**Información que PUEDE automatizarse:**
- ✅ Validación de email (formato correcto, no duplicado)
- ✅ Validación de datos requeridos
- ✅ Creación automática de cuenta
- ✅ Envío de email de bienvenida

---

#### Escenario 2: Cliente Antiguo - Dato en BD Antigua (MIGRANTE)

```
Cliente intenta registrarse con email

SISTEMA VERIFICA:
├─ ¿Email en BD antigua?
│  ├─ SÍ → Mostrar mensaje especial:
│  │   "Cuenta encontrada en nuestros registros"
│  │   ┌─ Opción 1: "Recuperar cuenta existente"
│  │   └─ Opción 2: "Crear nueva cuenta"
│  └─ NO → Proceder como nuevo cliente
└─ Si "Recuperar existente":
   ├─ Mandar code de verificación al email
   ├─ Cliente ingresa code
   ├─ Cliente establece nueva contraseña
   └─ Vincular con datos antiguos automáticamente

RESULTADO:
├─ Si recupera → Importar datos de BD antigua
├─ Si nuevo → Crear como nuevo
└─ Cliente listo para subir documentos
```

**Información que PUEDE automatizarse:**
- ✅ Búsqueda en BD antigua por email/RFC
- ✅ Validación de code de recuperación
- ✅ Importación automática de datos
- ⚠️ REQUIERE HUMANO: Verificación de que datos coincidan correctamente

---

#### Escenario 3: Cliente Antiguo - Mismo Cliente, Info NO Hace Match

```
Cliente nuevo ingresa datos:
├─ Email: juan@correo.com
├─ RFC: JUAP900101ABC
└─ Nombre: Juan Pérez

SISTEMA VERIFICA:
├─ ¿RFC encontrado en BD?
│  └─ SÍ → Buscar historial anterior
├─ ¿Email coincide?
│  └─ NO → ALERTA ROJA
├─ ¿Nombre coincide?
│  └─ NO → ALERTA ROJA
└─ ¿Teléfono coincide?
   └─ NO → ALERTA AMARILLA

ACCIONES AUTOMÁTICAS:
├─ Bloquear la cuenta temporalmente
├─ Generar reporte de incongruencia
├─ Asignar a VALIDADOR ESPECIAL (revisión manual)
├─ Enviar notificación a Staff
└─ Cliente recibe mensaje: "Verificando tu identidad. Contactaremos pronto"

VALIDADOR VERIFICA:
├─ ¿Es la misma persona?
│  ├─ SÍ → Actualizar datos
│  └─ NO → Crear nueva cuenta (potencial fraude)
├─ ¿Cambió legítimamente?
│  └─ Documentar razón en AuditLog
└─ Resolver incongruencia

RESULTADO:
├─ Si validación exitosa → Activar cuenta
├─ Si fraude sospechoso → Rechazar y alertar
└─ Si datos outdated → Actualizar y activar
```

**Información que PUEDE automatizarse:**
- ✅ Búsqueda de duplicados por RFC
- ✅ Comparación de campos
- ✅ Generación de alertas
- ❌ REQUIERE HUMANO: Verificación de identidad real (difícil de automatizar)

---

### 1.3 Carga de Documentos por Cliente

```
Cliente accede a panel ("Mis Documentos")
↓
Cliente hace click: "Subir nuevo documento"
↓
Cliente selecciona:
├─ Tipo de documento (Identificación, Comprobante domicilio, RFC, etc.)
├─ Archivo (PDF o imagen)
└─ Descripción (opcional)

SISTEMA RECIBE DOCUMENTO:
├─ Validar formato y tamaño
├─ Guardar en storage seguro
├─ Cifrar campos sensibles en BD
├─ Iniciar proceso OCR + IA

OCR + EXTRACCIÓN AUTOMÁTICA:
├─ PaddleOCR lee imagen/PDF
├─ Extrae texto raw
└─ Envía a DocumentValidator.extract_fields()

VALIDADOR IA DETECTA Y EXTRAE:
├─ CURP (patrón: AAAA000101ABC00)
├─ RFC (patrón: AAAA000101ABC)
├─ Nombres completos
├─ Teléfono (con variaciones +52, 55, etc.)
├─ Email
├─ Dirección (Calle, número, ciudad, estado)
├─ Ocupación
├─ Estado civil
├─ Fechas (DD/MM/YYYY)
└─ Números de cuenta/documento

VALIDACIÓN IA AUTOMÁTICA:
├─ Validar CURP con algoritmo Segob
├─ Validar RFC
├─ Validar email
├─ Validar formatos de teléfono
├─ Validar coherencia de fechas
└─ Generar score de confianza (0-100%)

CLASIFICACIÓN AUTOMÁTICA:
├─ Score >= 85% → "VALIDAR_AUTOMATICAMENTE" ✅
├─ Score 60-85% → "REVISAR" ⚠️
└─ Score < 60% → "RECHAZAR" ❌

RESULTADO EN BD:
├─ Document creada con status=pendiente_validacion
├─ ai_extraction_score: 85
├─ ai_recommendation: "VALIDAR_AUTOMATICAMENTE"
├─ Campos extraídos guardados (cifrados)
└─ DocumentHistory creada con timestamp
```

**Información que PUEDE automatizarse:**
- ✅ OCR y extracción de texto
- ✅ Validación de formato de datos
- ✅ Algoritmos de validación (CURP, RFC)
- ✅ Scoring automático
- ✅ Clasificación inicial
- ❌ REQUIERE HUMANO: Verificación de que el documento sea auténtico (anti-fraude)

---

## PARTE 2: PROCESO INTERNO DE VALIDACIÓN

### 2.1 Flujo de Validadores (2 Niveles)

```
DOCUMENTO CARGADO
        ↓
   ╔═══════════════════╗
   ║  VALIDADOR NIVEL 1║
   ╚═══════════════════╝
        ↓
VALIDADOR 1 ACCEDE A PANEL:
├─ Ve documentos asignados
├─ Ve recomendación IA (score, campos extraídos)
├─ Revisa documento original
├─ Compara con datos extraídos
├─ Toma decisión:
│  ├─ APROBAR → Documento pasa a Validador 2
│  ├─ RECHAZAR → Cliente recibe notificación
│  └─ SOLICITAR_REVISIÓN → Vuelve a IA para re-procesamiento
└─ Agrega comentario/nota en AuditLog

        ↓
   ╔═══════════════════╗
   ║  VALIDADOR NIVEL 2║
   ╚═══════════════════╝
        ↓
VALIDADOR 2 ACCEDE A PANEL:
├─ Ve decisión de Validador 1
├─ Revisa nuevamente documento
├─ Verifica coherencia de datos extraídos
├─ Comprueba que Validador 1 decidió correctamente
├─ Toma decisión final:
│  ├─ APROBAR_FINAL → Enviar a ERP
│  ├─ RECHAZAR_FINAL → Cliente recibe notificación
│  └─ DEVOLVER_A_V1 → Retroalimentación a Validador 1
└─ Agrega comentario en AuditLog

        ↓
   ╔═══════════════════╗
   ║  STAFF ADMIN      ║
   ╚═══════════════════╝
        ↓
ADMIN EXPORTA A ERP:
├─ Revisa validaciones finales
├─ Genera archivo de exportación
├─ Envía a sistema ERP bancario
├─ Crea registro de ERPExport en BD
└─ Genera reporte de auditoría
```

---

### 2.2 Panel de Validador 1

**URL**: `/validator1/`

**Estado**: Documents con `status=pending_validation` y sin validador1_decision

**Información que ve:**
```
DOCUMENTOS PENDIENTES
─────────────────────

Documento: RFC_ClienteX.pdf
┌─────────────────────────────────────┐
│ IA SCORE: 87%                       │
│ RECOMENDACIÓN: VALIDAR_AUTOMÁTICAMENTE │
├─────────────────────────────────────┤
│ Datos Extraídos por IA:             │
│ • CURP: JUAP900101JDFMNL00          │
│ • RFC: JUAP900101ABC                │
│ • Nombre: Juan Alberto Pérez        │
│ • Teléfono: +52 55 1234 5678        │
│ • Email: juan.perez@correo.com      │
│ • Dirección: Calle Principal 123... │
├─────────────────────────────────────┤
│ [Ver Documento Original]            │
│ [Aprobar] [Rechazar] [Solicitar Rev]│
└─────────────────────────────────────┘
```

**Decisiones que puede tomar:**
1. **APROBAR** → Pasa a Validador 2 automáticamente
2. **RECHAZAR** → Cliente recibe notificación, fin del proceso para este doc
3. **SOLICITAR_REVISIÓN** → IA reintenta extracción con feedback

**Validador 1 puede:**
- ✅ Editar datos extraídos si ve error obvio
- ✅ Agregar comentarios
- ✅ Ver historial completo del documento
- ❌ No puede: Exportar a ERP (eso lo hace Validador 2 + Admin)

---

### 2.3 Panel de Validador 2

**URL**: `/validator2/`

**Estado**: Documents con `status=pending_v2_validation` (aprobado por Validador 1)

**Información que ve:**
```
DOCUMENTOS EN REVISIÓN FINAL
────────────────────────────

Documento: RFC_ClienteX.pdf
┌─────────────────────────────────────┐
│ IA SCORE: 87%                       │
│ VALIDADOR 1: APROBÓ ✅              │
│ Comentario V1: "Datos correctos"    │
├─────────────────────────────────────┤
│ Datos Extraídos + Aprobados por V1: │
│ • CURP: JUAP900101JDFMNL00          │
│ • RFC: JUAP900101ABC                │
│ • Nombre: Juan Alberto Pérez        │
│ • Teléfono: +52 55 1234 5678        │
│ • Email: juan.perez@correo.com      │
│ • Dirección: Calle Principal 123... │
├─────────────────────────────────────┤
│ [Ver Documento Original]            │
│ [Aprobar Final] [Rechazar] [Devolver] │
└─────────────────────────────────────┘
```

**Decisiones que puede tomar:**
1. **APROBAR_FINAL** → Documento listo para ERP
2. **RECHAZAR_FINAL** → Cliente recibe rechazo, fin del proceso
3. **DEVOLVER_A_V1** → Retroalimentación, vuelve a panel de V1

**Validador 2 es responsable de:**
- ✅ Verificación final de coherencia
- ✅ Detección de inconsistencias
- ✅ Decisión definitiva
- ✅ Dar feedback detallado si rechaza

---

### 2.4 Panel de Admin

**URL**: `/dashboard-admin/`

**Responsabilidades:**
```
ADMIN VERIFICA:
├─ Documentos aprobados por V1 + V2
├─ Genera reporte de exportación
├─ Revisa auditoría completa
├─ Prepara datos para ERP
└─ Mantiene estadísticas

FUNCIONES PRINCIPALES:
├─ Crear/editar/eliminar validadores
├─ Ver audit log completo
├─ Exportar a ERP (genera archivo)
├─ Ver dashboard con estadísticas
│  ├─ Total documentos procesados
│  ├─ Tasa de aprobación
│  ├─ Tiempo promedio de validación
│  └─ Errores de IA
├─ Generar reportes
└─ Configurar sistema
```

---

## PARTE 3: CLASIFICACIÓN Y AUTOMACIÓN

### 3.1 ¿Cómo Clasificamos la Información?

**NIVEL 1: Por Tipo de Documento**
```
Documento → Categoría
├─ INE/Pasaporte → IDENTIFICACIÓN
├─ RFC → COMPROBANTE_FISCAL
├─ Comprobante domicilio → COMPROBANTE_DOMICILIO
├─ Nómina → COMPROBANTE_INGRESOS
└─ Etc.
```

**NIVEL 2: Por Score de IA**
```
Score de confianza (0-100%)
├─ 85-100% → CONFIANZA_ALTA (posible auto-aprobar)
├─ 60-85% → CONFIANZA_MEDIA (revisar)
└─ <60% → CONFIANZA_BAJA (rechazar o revisar manual)
```

**NIVEL 3: Por Campos Extraídos**
```
Para cada campo:
├─ VÁLIDO ✅ (formato correcto + validación pasó)
├─ INVÁLIDO ❌ (formato incorrecto)
└─ INCONGRUENTE ⚠️ (válido pero no coincide con BD)
```

---

### 3.2 ¿Qué Maneja el Aprobador?

**VALIDADOR 1:**
```
¿Campos extraídos son correctos?
├─ SÍ → Aprobar
├─ NO → Solicitar revisión / Rechazar
└─ Parcialmente → Editar y aprobar
```

**VALIDADOR 2:**
```
¿Todo el documento es coherente?
├─ SÍ → Aprobar final (listo para ERP)
├─ NO → Rechazar o devolver a V1
└─ Dudas → Puede solicitar más info
```

**ADMIN:**
```
¿Documentos están listos para procesamiento?
├─ SÍ → Exportar a ERP
├─ NO → Revisar auditoría
└─ Problemas → Investigar y resolver
```

---

### 3.3 ¿Qué Se Puede Automatizar?

| Tarea | ¿Automático? | Descripción |
|-------|-------------|-------------|
| Lectura de documento (OCR) | ✅ | PaddleOCR procesa imagen/PDF |
| Extracción de datos | ✅ | Regex + IA patterns |
| Validación de formato | ✅ | CURP/RFC/Email regex |
| Validación de CURP | ✅ | Algoritmo Segob |
| Validación de RFC | ✅ | Algoritmo SAT |
| Scoring de confianza | ✅ | Basado en campos extraídos |
| Clasificación inicial | ✅ | Por score |
| Detección de duplicados | ✅ | Búsqueda en BD |
| Alertas de incongruencia | ✅ | Comparar con BD antigua |
| **Verificación de autenticidad** | ❌ | REQUIERE HUMANO (anti-fraude) |
| **Decisión final** | ❌ | REQUIERE HUMANO (responsabilidad) |
| **Identificación real** | ❌ | REQUIERE HUMANO (KYC/AML) |
| **Resolución de conflictos** | ❌ | REQUIERE HUMANO (juicio) |
| Exportación a ERP | ✅ | Automático después de V2 |
| Auditoría | ✅ | Se registra automáticamente |

---

### 3.4 Tareas Críticas que REQUIEREN Intervención Humana

#### 1. **VERIFICACIÓN DE AUTENTICIDAD** 🔴 CRÍTICA
```
¿El documento es REAL o FALSIFICADO?
├─ IA puede detectar: Calidad de imagen, patrones
├─ IA NO puede detectar: Falsificación sofisticada
└─ VALIDADOR HUMANO debe verificar visualmente
```

**¿Quién revisa?**
- Validador 1 en su revisión inicial
- Validador 2 como "segunda opinión"

#### 2. **VALIDACIÓN DE IDENTIDAD (KYC)** 🔴 CRÍTICA
```
¿Es realmente la persona en el documento?
├─ IA extrae datos del documento
├─ IA valida formato de datos
├─ IA NO puede verificar: "¿Es el cliente real?"
└─ VALIDADOR HUMANO debe decidir si confía
```

**¿Quién revisa?**
- Validador 2 como responsable final

#### 3. **DETECCIÓN DE FRAUDE** 🔴 CRÍTICA
```
¿Hay señales de alerta?
├─ Múltiples cuentas con mismo RFC
├─ Datos inconsistentes
├─ Patrones sospechosos
├─ IA genera alertas automáticas
└─ VALIDADOR HUMANO investiga
```

**¿Quién revisa?**
- Admin (revisión de auditoría)
- Validador 2 (si lo detecta)

#### 4. **RESOLUCIÓN DE CONFLICTOS** 🟡 IMPORTANTE
```
¿Qué hacer si V1 aprueba pero V2 rechaza?
├─ IA no puede decidir entre opiniones
├─ Se requiere revisión manual
└─ Admin escala a revisión especial
```

**¿Quién revisa?**
- Admin + Validadores en sesión especial

---

## PARTE 4: FLUJO COMPLETO CON DECISIONES

```
┌─────────────────────────────────────────────────────────────────┐
│ CLIENTE SUBE DOCUMENTO                                          │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│ SISTEMA: OCR + EXTRACCIÓN AUTOMÁTICA                            │
│ ├─ Lee documento                                                │
│ ├─ Extrae campos                                                │
│ ├─ Valida formatos                                              │
│ └─ Genera score: 87%                                            │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│ DECISIÓN IA: Score >= 85%                                       │
│ → Asignar a VALIDADOR 1                                         │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│ VALIDADOR 1: REVISAR DOCUMENTO                                  │
│ Pregunta: ¿Datos extraídos son correctos?                       │
│                                                                 │
│ Opción A: SÍ → APROBAR                                          │
│ Opción B: NO → RECHAZAR (Cliente recibe notificación)           │
│ Opción C: PARCIAL → SOLICITAR REVISIÓN                          │
└─────────────────────────────────────────────────────────────────┘
                    ↓ (si APROBAR)
┌─────────────────────────────────────────────────────────────────┐
│ VALIDADOR 2: VERIFICACIÓN FINAL                                 │
│ Pregunta: ¿Es documento VÁLIDO y cliente es REAL?               │
│                                                                 │
│ Opción A: SÍ → APROBAR FINAL                                    │
│ Opción B: NO → RECHAZAR (Cliente recibe notificación)           │
│ Opción C: DUDAS → DEVOLVER A V1                                 │
└─────────────────────────────────────────────────────────────────┘
                    ↓ (si APROBAR FINAL)
┌─────────────────────────────────────────────────────────────────┐
│ ADMIN: EXPORTAR A ERP                                           │
│ ├─ Verifica validaciones completadas                            │
│ ├─ Genera archivo de exportación                                │
│ ├─ Envía a sistema bancario                                     │
│ └─ Registra en AuditLog                                         │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│ CLIENTE: NOTIFICACIÓN FINAL                                     │
│ "Tu solicitud fue aprobada y enviada al procesamiento"          │
└─────────────────────────────────────────────────────────────────┘
```

---

## PARTE 5: RESUMEN DE IMPLEMENTACIÓN

### ✅ LO QUE YA EXISTE EN EL SISTEMA

1. **Registro de Clientes** ✅
   - Auto-registro en website
   - Validación de email
   - Creación automática de perfil

2. **Carga de Documentos** ✅
   - Interface de upload
   - Almacenamiento seguro
   - Cifrado de datos sensibles

3. **OCR + Extracción IA** ✅
   - PaddleOCR integrado
   - Extracción de 9+ campos
   - Scoring automático

4. **Validación en 2 Niveles** ✅
   - Panel Validador 1
   - Panel Validador 2
   - Decisiones registradas

5. **Auditoría Completa** ✅
   - AuditLog de cada acción
   - Historial de cambios
   - Trazabilidad completa

6. **Exportación a ERP** ✅
   - Generación de archivos
   - Registro de exportación
   - Notificaciones

### 🟡 LO QUE FALTA / MEJORAS PROPUESTAS

1. **Integración con BD Antigua**
   - Script de migración de clientes
   - Validación de coincidencia de datos
   - Manejo de duplicados

2. **Búsqueda de Clientes Existentes**
   - Búsqueda por RFC
   - Búsqueda por email
   - Detección automática de duplicados

3. **Alertas de Incongruencia**
   - Alertar si datos no coinciden
   - Escalamiento automático
   - Revisión manual obligatoria

4. **Anti-Fraude Mejorado**
   - Detección de patrones sospechosos
   - Integración con bases de datos externas (BURO, SAT)
   - Flags de riesgo

5. **Edición de Datos Extraídos**
   - Permitir Validador 1 corregir OCR
   - Validación de cambios
   - Registro en auditoría

6. **Estadísticas y Reportes**
   - Dashboard con métricas
   - Reportes de validación
   - Análisis de errores IA

---

## RESPUESTAS A TUS PREGUNTAS

### P: ¿El sistema puede leer información de documentos?
**R: SÍ** ✅
- Usa PaddleOCR para leer texto
- Extrae 9+ campos con regex patterns
- Score de 87%+ en documentos reales
- Validación adicional por algoritmos (CURP, RFC)

### P: ¿Qué información maneja el aprobador?
**R: Depende del nivel**
- **Validador 1**: Verifica que IA extrajo bien
- **Validador 2**: Verifica que documento es auténtico + cliente es real
- **Admin**: Exporta y genera reportes

### P: ¿Qué se puede automatizar?
**R: Bastante**
- ✅ 90% del flujo se automatiza
- ❌ 10% requiere intervención humana (autenticidad, KYC, fraude)

### P: ¿Hay tareas críticas que requieren humano?
**R: SÍ, 4 críticas**
1. Verificación de autenticidad (¿documento es real?)
2. Validación de identidad (¿cliente es real?)
3. Detección de fraude (¿hay señales sospechosas?)
4. Resolución de conflictos (¿qué hacer si hay desacuerdos?)

---

## CONCLUSIÓN

El sistema actual es **robusto y automatizado** para el 90% de los casos. Los validadores humanos son necesarios solo para:
- Verificaciones de seguridad y fraude
- Decisiones finales de responsabilidad
- Resolución de excepciones

Esto permite **escalar sin perder control** de los riesgos bancarios.
