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

## Relaciones

```
Docente ←──┐
           │
           ├──→ Cargo ──→ Movimiento ←──→ Facepres
           │
Catedra ←──┘
```

## Configuración del Admin

El Django admin está configurado con:
- Registro simple para: Catedra, Docente, Cargo, Movimiento
- **FacepresAdmin**: Admin personalizado con inline de Movimiento
  - `MovimientoInline`: TabularInline para gestionar movimientos dentro de Facepres
  - Ver: `autoface/admin.py:11-18`

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
```

## Notas de Desarrollo

- La relación ManyToMany entre Facepres y Movimiento permite que múltiples movimientos estén asociados a un facepres
- Todos los ForeignKeys usan `on_delete=models.PROTECT` para evitar eliminación accidental de datos relacionados
- El inline admin facilita la gestión de movimientos directamente desde la interfaz de Facepres
