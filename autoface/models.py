from django.db import models


class Catedra(models.Model):
    codigo = models.CharField(max_length=200)
    nombre = models.CharField(max_length=200)


class Docente(models.Model):
    legajo = models.CharField(max_length=200)
    nombre = models.CharField(max_length=200)
    apellido = models.CharField(max_length=200)
    dni = models.CharField(max_length=200)


class Cargo(models.Model):
    codigo = models.CharField(max_length=200)
    estado = models.CharField(max_length=200)
    puntos = models.IntegerField(default=0)
    docente = models.ForeignKey(Docente, on_delete=models.PROTECT)
    catedra = models.ForeignKey(Catedra, on_delete=models.PROTECT)