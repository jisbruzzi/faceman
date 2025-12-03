from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from datetime import datetime
from .models import (Cargo, Catedra, Docente, Facepres, Movimiento,
                     ConciliacionMensual, RegistroLiquidacion, Discrepancia)

admin.site.register(Catedra)
admin.site.register(Docente)
admin.site.register(Cargo)
admin.site.register(Movimiento)


class MovimientoInline(admin.TabularInline):
    model = Facepres.movimientos.through
    extra = 1

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "movimiento":
            if hasattr(request, 'facepres_obj') and request.facepres_obj is not None:
                # Editando: excluir movimientos asignados a otros facepres
                otros_facepres = Facepres.objects.exclude(id=request.facepres_obj.id)
                movimientos_otros = Facepres.movimientos.through.objects.filter(
                    facepres__in=otros_facepres
                ).values_list('movimiento_id', flat=True)
                kwargs["queryset"] = Movimiento.objects.exclude(id__in=movimientos_otros)
            else:
                # Creando nuevo: excluir movimientos ya asignados
                movimientos_asignados = Facepres.movimientos.through.objects.values_list(
                    'movimiento_id', flat=True
                )
                kwargs["queryset"] = Movimiento.objects.exclude(id__in=movimientos_asignados)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Facepres)
class FacepresAdmin(admin.ModelAdmin):
    inlines = [MovimientoInline]
    exclude = ['movimientos']

    def get_form(self, request, obj=None, **kwargs):
        # Guardar el objeto actual en el request para usarlo en el inline
        request.facepres_obj = obj
        return super().get_form(request, obj, **kwargs)


# MÓDULO 4: Conciliación Mensual

class DiscrepanciaInline(admin.TabularInline):
    model = Discrepancia
    extra = 0
    readonly_fields = ['tipo', 'descripcion', 'puntos_esperados',
                      'puntos_liquidados', 'cargo', 'registro_liquidacion']
    fields = ['tipo', 'descripcion', 'estado', 'comentario_revision',
              'revisado_por', 'fecha_revision']

    def has_add_permission(self, request, obj=None):
        return False  # No crear manualmente, se generan automáticamente


class RegistroLiquidacionInline(admin.TabularInline):
    model = RegistroLiquidacion
    extra = 0
    readonly_fields = ['legajo', 'nombre_completo', 'codigo_cargo',
                      'puntos_liquidados', 'estado_matching']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(ConciliacionMensual)
class ConciliacionMensualAdmin(admin.ModelAdmin):
    list_display = ['periodo_formateado', 'estado', 'total_registros',
                   'coincidencias_badge', 'discrepancias_badge',
                   'fecha_carga', 'usuario_carga']
    list_filter = ['estado', 'periodo']
    readonly_fields = ['total_registros', 'total_coincidencias',
                      'total_discrepancias', 'fecha_carga', 'usuario_carga']
    inlines = [DiscrepanciaInline, RegistroLiquidacionInline]

    actions = ['procesar_conciliacion']

    def periodo_formateado(self, obj):
        return obj.periodo.strftime('%B %Y')
    periodo_formateado.short_description = 'Período'

    def coincidencias_badge(self, obj):
        if obj.total_coincidencias > 0:
            return format_html(
                '<span style="background-color: #28a745; color: white; '
                'padding: 3px 10px; border-radius: 3px;">✓ {}</span>',
                obj.total_coincidencias
            )
        return '-'
    coincidencias_badge.short_description = 'Coincidencias'

    def discrepancias_badge(self, obj):
        if obj.total_discrepancias > 0:
            return format_html(
                '<span style="background-color: #dc3545; color: white; '
                'padding: 3px 10px; border-radius: 3px;">⚠ {}</span>',
                obj.total_discrepancias
            )
        return '-'
    discrepancias_badge.short_description = 'Discrepancias'

    def save_model(self, request, obj, form, change):
        if not change:  # Nuevo objeto
            obj.usuario_carga = request.user
        super().save_model(request, obj, form, change)

    def procesar_conciliacion(self, request, queryset):
        """Acción para procesar Excels y generar comparación"""
        for conciliacion in queryset:
            if conciliacion.estado != 'PENDIENTE':
                messages.warning(request,
                    f'Conciliación {conciliacion} ya fue procesada')
                continue

            try:
                self._procesar_excel(conciliacion)
                messages.success(request,
                    f'Conciliación {conciliacion} procesada exitosamente. '
                    f'Coincidencias: {conciliacion.total_coincidencias}, '
                    f'Discrepancias: {conciliacion.total_discrepancias}')
            except Exception as e:
                messages.error(request, f'Error procesando {conciliacion}: {e}')

    procesar_conciliacion.short_description = "Procesar conciliación(es)"

    def _procesar_excel(self, conciliacion):
        """Lógica principal de comparación"""
        try:
            import openpyxl
        except ImportError:
            raise Exception("openpyxl no está instalado. Ejecute: pip install openpyxl")

        # 1. Leer Excel
        wb = openpyxl.load_workbook(conciliacion.archivo_excel)
        ws = wb.active

        registros_creados = 0
        coincidencias = 0
        discrepancias_count = 0

        # 2. Procesar cada fila (asumiendo formato: legajo, nombre, codigo, puntos)
        for row in ws.iter_rows(min_row=2, values_only=True):
            if not row[0]:  # Skip empty rows
                continue

            legajo = str(row[0]).strip()
            nombre = str(row[1]).strip()
            codigo = str(row[2]).strip()
            puntos = int(row[3])

            # Crear registro
            registro = RegistroLiquidacion.objects.create(
                conciliacion=conciliacion,
                legajo=legajo,
                nombre_completo=nombre,
                codigo_cargo=codigo,
                puntos_liquidados=puntos
            )
            registros_creados += 1

            # 3. Buscar en sistema
            try:
                docente = Docente.objects.get(legajo=legajo)
                cargo = Cargo.objects.get(
                    docente=docente,
                    codigo=codigo,
                    estado='LIQUIDADO'
                )
                registro.cargo_sistema = cargo

                # 4. Comparar puntos
                if cargo.puntos == puntos:
                    registro.estado_matching = 'OK'
                    coincidencias += 1
                else:
                    registro.estado_matching = 'DISCREPANCIA'
                    discrepancias_count += 1

                    # Crear discrepancia
                    Discrepancia.objects.create(
                        conciliacion=conciliacion,
                        tipo='DIFERENCIA_PUNTOS',
                        cargo=cargo,
                        registro_liquidacion=registro,
                        descripcion=f'Puntos diferentes para {nombre} (legajo {legajo}). '
                                  f'Sistema: {cargo.puntos}, Liquidado: {puntos}',
                        puntos_esperados=cargo.puntos,
                        puntos_liquidados=puntos
                    )

            except Docente.DoesNotExist:
                registro.estado_matching = 'DISCREPANCIA'
                discrepancias_count += 1

                Discrepancia.objects.create(
                    conciliacion=conciliacion,
                    tipo='CARGO_NO_ENCONTRADO',
                    registro_liquidacion=registro,
                    descripcion=f'Docente {nombre} (legajo {legajo}) no encontrado en sistema'
                )

            except Cargo.DoesNotExist:
                registro.estado_matching = 'DISCREPANCIA'
                discrepancias_count += 1

                Discrepancia.objects.create(
                    conciliacion=conciliacion,
                    tipo='PAGO_SIN_AUTORIZACION',
                    registro_liquidacion=registro,
                    descripcion=f'Se pagó cargo {codigo} a {nombre} sin autorización en sistema'
                )

            registro.save()

        # 5. Verificar cargos autorizados que NO fueron pagados
        cargos_liquidados = Cargo.objects.filter(estado='LIQUIDADO')
        for cargo in cargos_liquidados:
            existe_en_excel = RegistroLiquidacion.objects.filter(
                conciliacion=conciliacion,
                cargo_sistema=cargo
            ).exists()

            if not existe_en_excel:
                discrepancias_count += 1
                Discrepancia.objects.create(
                    conciliacion=conciliacion,
                    tipo='NO_PAGO_AUTORIZADO',
                    cargo=cargo,
                    descripcion=f'Cargo {cargo.codigo} de {cargo.docente.apellido}, '
                              f'{cargo.docente.nombre} no fue liquidado'
                )

        # 6. Actualizar métricas
        conciliacion.total_registros = registros_creados
        conciliacion.total_coincidencias = coincidencias
        conciliacion.total_discrepancias = discrepancias_count
        conciliacion.estado = 'PROCESADA'
        conciliacion.save()


@admin.register(Discrepancia)
class DiscrepanciaAdmin(admin.ModelAdmin):
    list_display = ['conciliacion', 'tipo', 'descripcion_corta',
                   'estado', 'revisado_por', 'fecha_revision']
    list_filter = ['tipo', 'estado', 'conciliacion']
    search_fields = ['descripcion', 'cargo__docente__apellido']
    readonly_fields = ['conciliacion', 'tipo', 'cargo',
                      'registro_liquidacion', 'descripcion',
                      'puntos_esperados', 'puntos_liquidados']

    actions = ['marcar_como_revisada']

    fieldsets = (
        ('Información de la Discrepancia', {
            'fields': ('conciliacion', 'tipo', 'descripcion',
                      'cargo', 'registro_liquidacion')
        }),
        ('Detalles de Puntos', {
            'fields': ('puntos_esperados', 'puntos_liquidados'),
            'classes': ('collapse',)
        }),
        ('Revisión', {
            'fields': ('estado', 'comentario_revision',
                      'revisado_por', 'fecha_revision')
        }),
    )

    def descripcion_corta(self, obj):
        return obj.descripcion[:60] + '...' if len(obj.descripcion) > 60 \
               else obj.descripcion
    descripcion_corta.short_description = 'Descripción'

    def marcar_como_revisada(self, request, queryset):
        for disc in queryset:
            disc.estado = 'REVISADA'
            disc.revisado_por = request.user
            disc.fecha_revision = datetime.now()
            disc.save()

        messages.success(request,
            f'{queryset.count()} discrepancia(s) marcada(s) como revisada(s)')

    marcar_como_revisada.short_description = "Marcar como revisada"
