from django.contrib import admin
from .models import Cargo, Catedra, Docente, Facepres, Movimiento

admin.site.register(Catedra)
admin.site.register(Docente)
admin.site.register(Cargo)

admin.site.register(Movimiento)
admin.site.register(Facepres)
