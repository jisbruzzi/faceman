# Instrucciones para Probar el Módulo 4 de Conciliación

## Preparación

Ya se han creado automáticamente:
- ✓ 5 docentes con cargos liquidados
- ✓ 3 cátedras
- ✓ 1 archivo Excel de prueba: `liquidacion_noviembre_2025_prueba.xlsx`

## Paso 1: Iniciar el servidor

```bash
python manage.py runserver
```

## Paso 2: Acceder al Django Admin

1. Abrir navegador en: http://localhost:8000/admin/
2. Iniciar sesión con tu superusuario
   - Si no tienes uno: `python manage.py createsuperuser`

## Paso 3: Explorar los datos existentes

### Ver Docentes:
1. Click en **Docentes** en el admin
2. Deberías ver 5-7 docentes, incluyendo:
   - García, Juan (12345)
   - López, María (67890)
   - Fernández, Carlos (11111)
   - Martínez, Ana (22222)
   - Rodríguez, Luis (33333)

### Ver Cargos:
1. Click en **Cargos** en el admin
2. Filtrar por estado: **LIQUIDADO**
3. Deberías ver 5 cargos liquidados

## Paso 4: Crear una Conciliación

1. En el menú del admin, buscar **Conciliaciones mensuales**
2. Click en **Agregar Conciliación Mensual**
3. Completar el formulario:
   - **Período**: Seleccionar 01/11/2025 (Noviembre 2025)
   - **Archivo excel**: Click en "Elegir archivo"
   - Buscar el archivo: `liquidacion_noviembre_2025_prueba.xlsx`
4. Click en **Guardar**

**Resultado esperado:**
- La conciliación se crea en estado **PENDIENTE**
- Los campos de métricas están en 0

## Paso 5: Procesar la Conciliación

1. En el listado de **Conciliaciones mensuales**
2. Marcar el checkbox de la conciliación recién creada
3. En el menú desplegable **Acción**, seleccionar: **Procesar conciliación(es)**
4. Click en **Ir**

**Resultado esperado:**
- Mensaje de éxito en verde en la parte superior
- Ver: "Conciliación ... procesada exitosamente. Coincidencias: 3, Discrepancias: 4"

## Paso 6: Ver los Resultados

1. Click en la conciliación procesada para ver el detalle
2. Observar:
   - **Estado**: cambió a **PROCESADA**
   - **Total registros**: 6
   - Badge verde **✓ 3** (coincidencias)
   - Badge rojo **⚠ 4** (discrepancias)

### Ver las Discrepancias (inline):

Deberías ver 4 discrepancias:

1. **Diferencia en puntos**:
   - Martínez, Ana (22222) - Cargo 342
   - Sistema: 50000 pts, Liquidado: 45000 pts

2. **Cargo no encontrado en sistema** (2 casos):
   - Pérez, Roberto (99999) - Docente no encontrado
   - García, Juan - Cargo 888 sin autorización

3. **No se pagó cargo autorizado**:
   - Rodríguez, Luis (33333) - Cargo 654 - 12000 pts
   - (Está autorizado pero NO aparece en el Excel)

### Ver los Registros de Liquidación (inline):

Deberías ver 6 registros del Excel con su estado:
- 3 con estado **OK** (coincidencias)
- 3 con estado **DISCREPANCIA**

## Paso 7: Revisar Discrepancias

### Opción A: Desde la Conciliación

1. Scroll down hasta **Discrepancias**
2. Para cada discrepancia, agregar comentarios en línea
3. No se pueden modificar los campos readonly (tipo, descripción, puntos)

### Opción B: Desde el Admin de Discrepancias

1. Ir al menú principal → **Discrepancias**
2. Ver todas las discrepancias
3. Usar filtros:
   - Por **Tipo**
   - Por **Estado**
   - Por **Conciliación**
4. Click en una discrepancia para ver detalles
5. Agregar **Comentario de revisión**, ejemplo:
   ```
   Diferencia de puntos verificada. El docente tuvo una reducción
   de dedicación en Octubre que no fue registrada en el sistema.
   Actualizar cargo en próxima sesión.
   ```

## Paso 8: Marcar Discrepancias como Revisadas

### Método Batch:
1. En el listado de **Discrepancias**
2. Seleccionar una o más discrepancias
3. Acción: **Marcar como revisada**
4. Click en **Ir**

**Resultado esperado:**
- Las discrepancias cambian a estado **REVISADA**
- Se registra automáticamente:
  - Tu usuario como "revisado_por"
  - Fecha y hora actual

### Método Individual:
1. Abrir una discrepancia
2. Cambiar **Estado** a: **REVISADA**
3. Agregar **Comentario de revisión**
4. **Guardar**

## Paso 9: Finalizar Conciliación

1. Volver a la **Conciliación Mensual**
2. Verificar que todas las discrepancias estén revisadas
3. Cambiar el **Estado** de la conciliación a: **REVISADA**
4. **Guardar**

## Resultados Finales Esperados

### Dashboard de Conciliación:
```
Período: Noviembre 2025
Estado: REVISADA
Total registros: 6
✓ 3 Coincidencias
⚠ 4 Discrepancias (todas revisadas)
```

### Casos Cubiertos:
- ✓ Coincidencias perfectas (3)
- ✓ Diferencia de puntos (1)
- ✓ Pago sin autorización (2)
- ✓ No se pagó cargo autorizado (1)
- ✓ Workflow completo de revisión

## Troubleshooting

### Error: "openpyxl no está instalado"
```bash
pip install openpyxl
```

### No se ve el archivo Excel al subirlo
- Verificar que MEDIA_ROOT esté configurado en settings.py
- Verificar permisos de la carpeta `media/`

### El Excel no se procesa correctamente
1. Verificar que el formato sea:
   - Columna A: Legajo
   - Columna B: Nombre
   - Columna C: Código Cargo
   - Columna D: Puntos
2. Primera fila = encabezados (se ignora)
3. Datos empiezan en fila 2

## Próximos Pasos

Después de probar con este Excel:

1. **Crear otro Excel** con tus propios datos:
   ```bash
   # Editar generar_excel_prueba.py con tus datos
   python generar_excel_prueba.py
   ```

2. **Agregar más docentes y cargos**:
   ```bash
   # Editar crear_datos_prueba.py
   python crear_datos_prueba.py
   ```

3. **Probar casos edge**:
   - Excels con muchos registros (100+)
   - Excels con formato diferente
   - Múltiples conciliaciones en diferentes períodos

## Scripts Útiles

### Regenerar datos de prueba:
```bash
python crear_datos_prueba.py
```

### Regenerar Excel de prueba:
```bash
python generar_excel_prueba.py
```

### Limpiar base de datos (CUIDADO):
```bash
# Eliminar y recrear base de datos
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
python crear_datos_prueba.py
```

## Documentación Adicional

- **MODULO4_CONCILIACION.md** - Guía completa de uso
- **CLAUDE.md** - Documentación técnica del proyecto
