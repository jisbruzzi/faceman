#!/usr/bin/env python
"""
Script para crear datos de prueba en la base de datos
Ejecutar: python crear_datos_prueba.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'faceman.settings')
django.setup()

from autoface.models import Catedra, Docente, Cargo

def crear_datos_prueba():
    print("Creando datos de prueba...")

    # Crear cátedras
    catedras = [
        Catedra.objects.get_or_create(codigo="MAT-101", nombre="Matemática I")[0],
        Catedra.objects.get_or_create(codigo="FIS-201", nombre="Física II")[0],
        Catedra.objects.get_or_create(codigo="QUI-301", nombre="Química General")[0],
    ]
    print(f"✓ Creadas {len(catedras)} cátedras")

    # Crear docentes
    docentes_data = [
        ("12345", "Juan", "García", "20123456"),
        ("67890", "María", "López", "27678901"),
        ("11111", "Carlos", "Fernández", "30111111"),
        ("22222", "Ana", "Martínez", "25222222"),
        ("33333", "Luis", "Rodríguez", "28333333"),
    ]

    docentes = []
    for legajo, nombre, apellido, dni in docentes_data:
        docente, created = Docente.objects.get_or_create(
            legajo=legajo,
            defaults={'nombre': nombre, 'apellido': apellido, 'dni': dni}
        )
        docentes.append(docente)

    print(f"✓ Creados {len(docentes)} docentes")

    # Crear cargos LIQUIDADOS (que deberían aparecer en el Excel)
    cargos_liquidados = [
        # Estos coincidirán perfectamente con el Excel
        (docentes[0], catedras[0], "757", "LIQUIDADO", 18000),  # García - JTP Semi
        (docentes[1], catedras[1], "423", "LIQUIDADO", 25000),  # López - Profesor Asociado
        (docentes[2], catedras[2], "851", "LIQUIDADO", 6000),   # Fernández - Ayudante Simple

        # Este tendrá diferencia de puntos en el Excel
        (docentes[3], catedras[0], "342", "LIQUIDADO", 50000),  # Martínez - Titular (Excel tendrá 45000)

        # Este NO aparecerá en el Excel (generará discrepancia: no se pagó)
        (docentes[4], catedras[1], "654", "LIQUIDADO", 12000),  # Rodríguez - no liquidado
    ]

    cargos = []
    for docente, catedra, codigo, estado, puntos in cargos_liquidados:
        cargo, created = Cargo.objects.get_or_create(
            docente=docente,
            catedra=catedra,
            codigo=codigo,
            defaults={'estado': estado, 'puntos': puntos}
        )
        if not created:
            cargo.estado = estado
            cargo.puntos = puntos
            cargo.save()
        cargos.append(cargo)

    print(f"✓ Creados {len(cargos)} cargos en estado LIQUIDADO")

    # Crear algunos cargos VACANTES (para otros tests futuros)
    cargos_vacantes = [
        (docentes[0], catedras[1], "999", "VACANTE", 15000),
    ]

    for docente, catedra, codigo, estado, puntos in cargos_vacantes:
        cargo, created = Cargo.objects.get_or_create(
            docente=docente,
            catedra=catedra,
            codigo=codigo,
            defaults={'estado': estado, 'puntos': puntos}
        )
        if not created:
            cargo.estado = estado
            cargo.puntos = puntos
            cargo.save()

    print(f"✓ Creados {len(cargos_vacantes)} cargos en estado VACANTE")

    print("\n=== RESUMEN DE DATOS CREADOS ===")
    print(f"Total Cátedras: {Catedra.objects.count()}")
    print(f"Total Docentes: {Docente.objects.count()}")
    print(f"Total Cargos: {Cargo.objects.count()}")
    print(f"  - LIQUIDADOS: {Cargo.objects.filter(estado='LIQUIDADO').count()}")
    print(f"  - VACANTES: {Cargo.objects.filter(estado='VACANTE').count()}")

    print("\n=== DOCENTES CON CARGOS LIQUIDADOS ===")
    for cargo in Cargo.objects.filter(estado='LIQUIDADO'):
        print(f"  {cargo.docente.legajo} - {cargo.docente.apellido}, {cargo.docente.nombre} - Cargo {cargo.codigo} - {cargo.puntos} pts")

if __name__ == '__main__':
    crear_datos_prueba()
    print("\n✓ Datos de prueba creados exitosamente!")
