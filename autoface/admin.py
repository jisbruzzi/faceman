from django.contrib import admin
from .models import Cargo, Catedra, Docente, Facepres, Movimiento

admin.site.register(Catedra)
admin.site.register(Docente)
admin.site.register(Cargo)

admin.site.register(Movimiento)


class MovimientoInline(admin.TabularInline):
    model = Facepres.movimientos.through
    extra = 1


@admin.register(Facepres)
class FacepresAdmin(admin.ModelAdmin):
    inlines = [MovimientoInline]
    exclude = ['movimientos']
