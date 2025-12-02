from django.contrib import admin
from .models import Cargo, Catedra, Docente, Facepres, Movimiento

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
