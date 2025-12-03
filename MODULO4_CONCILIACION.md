# Módulo 4: Conciliación Mensual - Guía de Uso

## Descripción

El Módulo 4 de Conciliación Mensual permite comparar automáticamente los sueldos liquidados por el área de Haberes (Excel) con los cargos autorizados en el sistema Faceman.

## Flujo de Trabajo

### 1. Cargar Excel de Liquidación

1. Ir a **Django Admin** → **Conciliaciones Mensuales** → **Agregar Conciliación Mensual**
2. Completar:
   - **Período**: Mes/Año de la liquidación (ej: 01/11/2025 para Noviembre 2025)
   - **Archivo Excel**: Subir el archivo .xlsx recibido de Haberes
3. Click en **Guardar**

El sistema crea la conciliación en estado **PENDIENTE**.

### 2. Procesar Conciliación

1. En el listado de **Conciliaciones Mensuales**, seleccionar la(s) conciliación(es) pendiente(s)
2. En el menú desplegable de **Acciones**, seleccionar **Procesar conciliación(es)**
3. Click en **Ir**

El sistema automáticamente:
- Lee el Excel fila por fila
- Busca cada docente y cargo en el sistema
- Compara puntos liquidados vs autorizados
- Genera registros de liquidación
- Identifica y registra discrepancias
- Actualiza métricas (coincidencias/discrepancias)

### 3. Revisar Resultados

En la vista de detalle de la conciliación verás:

- **Badges de estado**:
  - ✓ Verde: Coincidencias (todo OK)
  - ⚠ Rojo: Discrepancias (requieren revisión)

- **Tabs inline**:
  - **Discrepancias**: Diferencias detectadas
  - **Registros de Liquidación**: Todas las filas del Excel

### 4. Gestionar Discrepancias

#### Tipos de Discrepancias:

1. **Se pagó sin autorización**: Cargo liquidado que no existe como LIQUIDADO en el sistema
2. **No se pagó cargo autorizado**: Cargo en estado LIQUIDADO que no aparece en el Excel
3. **Diferencia en puntos**: El cargo existe pero los puntos no coinciden
4. **Cargo no encontrado en sistema**: Docente no registrado en Faceman

#### Revisión:

1. Ir a **Discrepancias** en el admin
2. Filtrar por conciliación, tipo o estado
3. Abrir cada discrepancia
4. Analizar el problema
5. Agregar **Comentario de revisión** explicando:
   - Causa de la discrepancia
   - Acción tomada o pendiente
6. Seleccionar discrepancias resueltas
7. Acción → **Marcar como revisada**

### 5. Finalizar Conciliación

Una vez revisadas todas las discrepancias:
1. Cambiar estado de la conciliación a **REVISADA**
2. El proceso está completo

## Formato del Excel de Haberes

El sistema espera un archivo .xlsx con el siguiente formato:

| Legajo | Nombre Completo | Código Cargo | Puntos |
|--------|----------------|--------------|--------|
| 12345  | García, Juan   | 757          | 18000  |
| 67890  | López, María   | 423          | 25000  |

**Importante**: La primera fila es el encabezado y se ignora. Los datos comienzan en la fila 2.

### Ajustar Formato del Excel

Si el Excel de Haberes tiene un formato diferente, editar el método `_procesar_excel()` en `autoface/admin.py:147` ajustando los índices de columnas:

```python
# Actual:
legajo = str(row[0]).strip()    # Columna A
nombre = str(row[1]).strip()    # Columna B
codigo = str(row[2]).strip()    # Columna C
puntos = int(row[3])            # Columna D

# Ejemplo si cambian las columnas:
legajo = str(row[1]).strip()    # Ahora está en columna B
nombre = str(row[2]).strip()    # Ahora está en columna C
# etc...
```

## Casos de Uso

### Caso 1: Todo coincide

```
Resultado:
- 150 registros procesados
- ✓ 150 coincidencias
- ⚠ 0 discrepancias
Estado: PROCESADA → puede marcar como REVISADA directamente
```

### Caso 2: Se detectan diferencias

```
Resultado:
- 150 registros procesados
- ✓ 145 coincidencias
- ⚠ 5 discrepancias

Revisar las 5 discrepancias:
- 2x "Diferencia en puntos" → Verificar si hubo actualización no registrada
- 1x "Se pagó sin autorización" → Verificar con Haberes
- 1x "No se pagó autorizado" → Verificar licencia/suspensión
- 1x "Cargo no encontrado" → Puede ser un alta nueva no registrada
```

## Reportes y Consultas

### Consultas útiles en el admin:

- **Discrepancias pendientes**: Filtro Estado = PENDIENTE
- **Conciliaciones del año**: Filtro por Período (año actual)
- **Discrepancias por tipo**: Filtro Tipo + buscar por docente

## Validaciones Automáticas

El sistema valida:
1. Solo cargos en estado LIQUIDADO se consideran autorizados
2. Matching exacto por legajo + código de cargo
3. Comparación exacta de puntos (sin tolerancia)
4. Detección de pagos duplicados
5. Detección de cargos autorizados no liquidados

## Seguridad y Auditoría

Todos los cambios quedan registrados:
- Usuario que cargó la conciliación
- Fecha de carga
- Usuario que revisó cada discrepancia
- Fecha de revisión
- Comentarios de revisión

## Solución de Problemas

### Error: "openpyxl no está instalado"

```bash
pip install openpyxl
```

### Error al leer Excel: "list index out of range"

El formato del Excel no coincide con el esperado. Verificar:
1. Que tenga las 4 columnas: legajo, nombre, codigo, puntos
2. Que no haya filas vacías al principio
3. Ajustar los índices en `_procesar_excel()` si es necesario

### No se encuentran cargos que deberían existir

Verificar:
1. Que el legajo en el Excel coincida exactamente con el del sistema
2. Que el cargo esté en estado "LIQUIDADO"
3. Que el código de cargo sea exactamente igual

## Próximas Mejoras Sugeridas

- Exportar reporte de discrepancias a PDF/Excel
- Dashboard con gráficos de evolución mensual
- Alertas automáticas por email
- Configuración de tolerancia de puntos (±X%)
- Importación masiva de ajustes desde Excel
