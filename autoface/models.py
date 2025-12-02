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


class Movimiento(models.Model):
    tipo = models.CharField(max_length=200)
    cargo = models.ForeignKey(Cargo, on_delete=models.PROTECT)
    puntos = models.IntegerField(default=0)
    motivo = models.CharField(max_length=200)


class Facepres(models.Model):
    movimientos = models.ManyToManyField(Movimiento)
    numero = models.CharField(max_length=200)
    estado = models.CharField(max_length=200)
