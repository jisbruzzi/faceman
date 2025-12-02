from django.contrib import admin
from .models import Cargo, Catedra, Docente

admin.site.register(Catedra)
admin.site.register(Docente)
admin.site.register(Cargo)
