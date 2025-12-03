from django.db import models
from django.contrib.auth.models import User


class Catedra(models.Model):
    codigo = models.CharField(max_length=200)
    nombre = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Docente(models.Model):
    legajo = models.CharField(max_length=200)
    nombre = models.CharField(max_length=200)
    apellido = models.CharField(max_length=200)
    dni = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.apellido}, {self.nombre} ({self.legajo})"


class Cargo(models.Model):
    codigo = models.CharField(max_length=200)
    estado = models.CharField(max_length=200)
    puntos = models.IntegerField(default=0)
    docente = models.ForeignKey(Docente, on_delete=models.PROTECT)
    catedra = models.ForeignKey(Catedra, on_delete=models.PROTECT)

    def __str__(self):
        return f"Cargo {self.codigo} - {self.docente.apellido} ({self.estado})"


class Movimiento(models.Model):
    tipo = models.CharField(max_length=200)
    cargo = models.ForeignKey(Cargo, on_delete=models.PROTECT)
    puntos = models.IntegerField(default=0)
    motivo = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.tipo} - {self.puntos} pts"


class Facepres(models.Model):
    movimientos = models.ManyToManyField(Movimiento)
    numero = models.CharField(max_length=200)
    estado = models.CharField(max_length=200)

    def __str__(self):
        return f"FACEPRES {self.numero}"

    class Meta:
        verbose_name_plural = "Facepres"


# MÓDULO 4: Conciliación Mensual

class ConciliacionMensual(models.Model):
    """Representa una conciliación mensual del Excel de Haberes"""
    ESTADOS = [
        ('PENDIENTE', 'Pendiente de Procesar'),
        ('PROCESADA', 'Procesada'),
        ('REVISADA', 'Completamente Revisada'),
    ]

    periodo = models.DateField(help_text="Mes/Año de la liquidación")
    archivo_excel = models.FileField(upload_to='conciliaciones/')
    fecha_carga = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')

    # Métricas automáticas
    total_registros = models.IntegerField(default=0)
    total_coincidencias = models.IntegerField(default=0)
    total_discrepancias = models.IntegerField(default=0)

    usuario_carga = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self):
        return f"Conciliación {self.periodo.strftime('%m/%Y')}"

    class Meta:
        verbose_name = "Conciliación Mensual"
        verbose_name_plural = "Conciliaciones Mensuales"
        ordering = ['-periodo']


class RegistroLiquidacion(models.Model):
    """Cada fila del Excel de Haberes"""
    conciliacion = models.ForeignKey(ConciliacionMensual,
                                    on_delete=models.CASCADE,
                                    related_name='registros')

    # Datos del Excel
    legajo = models.CharField(max_length=200)
    nombre_completo = models.CharField(max_length=400)
    codigo_cargo = models.CharField(max_length=200)
    puntos_liquidados = models.IntegerField()

    # Matching con sistema
    cargo_sistema = models.ForeignKey(Cargo, on_delete=models.PROTECT,
                                     null=True, blank=True)
    estado_matching = models.CharField(max_length=20, default='PENDIENTE')

    def __str__(self):
        return f"{self.nombre_completo} - {self.codigo_cargo}"

    class Meta:
        verbose_name = "Registro de Liquidación"
        verbose_name_plural = "Registros de Liquidación"


class Discrepancia(models.Model):
    """Diferencias detectadas entre liquidación y sistema"""
    TIPOS = [
        ('PAGO_SIN_AUTORIZACION', 'Se pagó sin autorización'),
        ('NO_PAGO_AUTORIZADO', 'No se pagó cargo autorizado'),
        ('DIFERENCIA_PUNTOS', 'Diferencia en puntos'),
        ('CARGO_NO_ENCONTRADO', 'Cargo no encontrado en sistema'),
    ]

    ESTADOS_REVISION = [
        ('PENDIENTE', 'Pendiente Revisión'),
        ('REVISADA', 'Revisada'),
    ]

    conciliacion = models.ForeignKey(ConciliacionMensual,
                                    on_delete=models.CASCADE,
                                    related_name='discrepancias')
    tipo = models.CharField(max_length=30, choices=TIPOS)

    # Referencias
    cargo = models.ForeignKey(Cargo, on_delete=models.PROTECT,
                             null=True, blank=True)
    registro_liquidacion = models.ForeignKey(RegistroLiquidacion,
                                            on_delete=models.CASCADE,
                                            null=True, blank=True)

    # Detalles
    descripcion = models.TextField()
    puntos_esperados = models.IntegerField(null=True, blank=True)
    puntos_liquidados = models.IntegerField(null=True, blank=True)

    # Workflow de revisión
    estado = models.CharField(max_length=20, choices=ESTADOS_REVISION,
                             default='PENDIENTE')
    comentario_revision = models.TextField(blank=True)
    revisado_por = models.ForeignKey(User, on_delete=models.PROTECT,
                                    null=True, blank=True,
                                    related_name='discrepancias_revisadas')
    fecha_revision = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.conciliacion}"

    class Meta:
        verbose_name = "Discrepancia"
        verbose_name_plural = "Discrepancias"
        ordering = ['estado', '-fecha_revision']
