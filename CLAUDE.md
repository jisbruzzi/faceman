# Faceman - Sistema de Gestión de Facepres

## Descripción del Proyecto

Faceman es una aplicación Django para la gestión de facepres (presentismo de facultad), que maneja docentes, cátedras, cargos y movimientos asociados.

## Estructura del Proyecto

```
face/
├── autoface/           # App principal de Django
│   ├── admin.py       # Configuración del Django admin
│   ├── models.py      # Modelos de datos
│   ├── views.py       # Vistas
│   └── migrations/    # Migraciones de base de datos
├── faceman/           # Configuración del proyecto Django
│   └── settings.py    # Configuración principal
├── manage.py          # Script de gestión de Django
└── db.sqlite3         # Base de datos SQLite
```

## Modelos de Datos

### Catedra
- `codigo`: CharField (200)
- `nombre`: CharField (200)

### Docente
- `legajo`: CharField (200)
- `nombre`: CharField (200)
- `apellido`: CharField (200)
- `dni`: CharField (200)

### Cargo
- `codigo`: CharField (200)
- `estado`: CharField (200)
- `puntos`: IntegerField (default: 0)
- `docente`: ForeignKey → Docente (PROTECT)
- `catedra`: ForeignKey → Catedra (PROTECT)

### Movimiento
- `tipo`: CharField (200)
- `cargo`: ForeignKey → Cargo (PROTECT)
- `puntos`: IntegerField (default: 0)
- `motivo`: CharField (200)

### Facepres
- `movimientos`: ManyToManyField → Movimiento
- `numero`: CharField (200)
- `estado`: CharField (200)

### ConciliacionMensual (Módulo 4)
- `periodo`: DateField
- `archivo_excel`: FileField
- `estado`: CharField (PENDIENTE, PROCESADA, REVISADA)
- `total_registros`: IntegerField
- `total_coincidencias`: IntegerField
- `total_discrepancias`: IntegerField
- `usuario_carga`: ForeignKey → User (PROTECT)

### RegistroLiquidacion
- `conciliacion`: ForeignKey → ConciliacionMensual (CASCADE)
- `legajo`: CharField (200)
- `nombre_completo`: CharField (400)
- `codigo_cargo`: CharField (200)
- `puntos_liquidados`: IntegerField
- `cargo_sistema`: ForeignKey → Cargo (PROTECT, nullable)
- `estado_matching`: CharField (OK, DISCREPANCIA)

### Discrepancia
- `conciliacion`: ForeignKey → ConciliacionMensual (CASCADE)
- `tipo`: CharField (PAGO_SIN_AUTORIZACION, NO_PAGO_AUTORIZADO, DIFERENCIA_PUNTOS, CARGO_NO_ENCONTRADO)
- `cargo`: ForeignKey → Cargo (PROTECT, nullable)
- `registro_liquidacion`: ForeignKey → RegistroLiquidacion (CASCADE, nullable)
- `descripcion`: TextField
- `puntos_esperados`: IntegerField (nullable)
- `puntos_liquidados`: IntegerField (nullable)
- `estado`: CharField (PENDIENTE, REVISADA)
- `comentario_revision`: TextField
- `revisado_por`: ForeignKey → User (PROTECT, nullable)
- `fecha_revision`: DateTimeField (nullable)

## Relaciones

```
Docente ←──┐
           │
           ├──→ Cargo ──→ Movimiento ←──→ Facepres
           │              ↓
Catedra ←──┘              ↓
                          ↓ (validación)
                   ConciliacionMensual ──→ RegistroLiquidacion
                          ↓
                    Discrepancia
```

## Configuración del Admin

El Django admin está configurado con:

### Modelos Base
- Registro simple para: Catedra, Docente, Cargo, Movimiento
- **FacepresAdmin**: Admin personalizado con inline de Movimiento
  - `MovimientoInline`: TabularInline para gestionar movimientos dentro de Facepres
  - Ver: `autoface/admin.py:14-44`

### Módulo 4: Conciliación Mensual

- **ConciliacionMensualAdmin**: Admin personalizado para gestión de conciliaciones
  - `DiscrepanciaInline`: Muestra discrepancias detectadas (read-only)
  - `RegistroLiquidacionInline`: Muestra registros del Excel (read-only)
  - Acción personalizada: `procesar_conciliacion` - Lee Excel y compara con sistema
  - Badges visuales para coincidencias (✓ verde) y discrepancias (⚠ rojo)
  - Ver: `autoface/admin.py:72-244`

- **DiscrepanciaAdmin**: Admin para revisión de discrepancias
  - Acción personalizada: `marcar_como_revisada` - Marca discrepancias como revisadas
  - Fieldsets organizados por: Información, Detalles de Puntos, Revisión
  - Ver: `autoface/admin.py:247-289`

## Comandos Útiles

```bash
# Crear superusuario
python manage.py createsuperuser

# Aplicar migraciones
python manage.py migrate

# Crear migraciones después de cambios en models.py
python manage.py makemigrations autoface

# Ejecutar servidor de desarrollo
python manage.py runserver

# Instalar dependencias del Módulo 4
pip install openpyxl
```

## Dependencias

- **Django**: Framework web principal
- **openpyxl**: Lectura de archivos Excel (.xlsx) para el Módulo 4 de Conciliación

## Notas de Desarrollo

### General
- La relación ManyToMany entre Facepres y Movimiento permite que múltiples movimientos estén asociados a un facepres
- Todos los ForeignKeys usan `on_delete=models.PROTECT` para evitar eliminación accidental de datos relacionados
- El inline admin facilita la gestión de movimientos directamente desde la interfaz de Facepres

### Módulo 4: Conciliación Mensual
- Los archivos Excel se guardan en `media/conciliaciones/`
- El formato esperado del Excel: Legajo | Nombre | Código Cargo | Puntos
- La comparación se hace con cargos en estado "LIQUIDADO"
- Sistema de validación automático genera 4 tipos de discrepancias
- Workflow completo: PENDIENTE → PROCESADA → REVISADA
- Ver documentación completa en: `MODULO4_CONCILIACION.md`

## Archivos de Documentación

- **CLAUDE.md**: Documentación técnica del proyecto (este archivo)
- **MODULO4_CONCILIACION.md**: Guía de uso del Módulo 4 de Conciliación Mensual
