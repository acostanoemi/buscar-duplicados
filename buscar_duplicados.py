#!/usr/bin/env python3
"""
Buscador de archivos duplicados - v3

Recorre una carpeta (y sus subcarpetas) y encuentra archivos con contenido
IDENTICO, aunque tengan nombres distintos. Por defecto solo los LISTA.

Como funciona:
  1. Agrupa los archivos por TAMAÑO (dato gratis, el sistema ya lo sabe).
  2. Solo hashea los que comparten tamaño con otro: si un tamaño es unico,
     ese archivo no puede tener duplicado, y no hace falta leerlo. Asi se
     evita hashear casi todos los archivos -> mucho mas rapido.
  3. Agrupa por hash los que quedaron: mismo hash = mismo contenido.

Al borrar, podés elegir CUAL copia conservar de cada grupo (--conservar).

Uso:
    python3 buscar_duplicados.py                      # busca en ~/Descargas
    python3 buscar_duplicados.py ~/Imagenes           # en otra carpeta
    python3 buscar_duplicados.py ~/fotos --borrar     # listar y ofrecer borrar
    python3 buscar_duplicados.py ~/fotos --borrar --conservar antiguo
"""

import hashlib
import argparse
from pathlib import Path
from collections import defaultdict


def parsear_args():
    p = argparse.ArgumentParser(
        description="Encuentra archivos duplicados (mismo contenido) en una carpeta."
    )
    p.add_argument("carpeta", nargs="?", default=str(Path.home() / "Descargas"),
                   help="carpeta donde buscar (default: ~/Descargas)")
    p.add_argument("--borrar", action="store_true",
                   help="despues de listar, ofrece borrar las copias")
    p.add_argument("--conservar", choices=["primero", "corto", "antiguo", "nuevo"],
                   default="primero",
                   help="cual copia conservar de cada grupo al borrar "
                        "(primero=como aparece, corto=nombre mas corto, "
                        "antiguo=mas viejo, nuevo=mas reciente). Default: primero")
    return p.parse_args()


def hash_archivo(ruta, bloque=65536):
    """Calcula el hash SHA-256 del contenido, leyendo de a bloques."""
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        while True:
            datos = f.read(bloque)
            if not datos:
                break
            h.update(datos)
    return h.hexdigest()


def agrupar_duplicados(base):
    """
    Devuelve una lista de grupos; cada grupo es una lista de archivos identicos.
    Optimizacion: solo hashea archivos que comparten tamaño con otro.
    """
    # Paso 1: agrupar por tamaño (gratis)
    por_tamano = defaultdict(list)
    for archivo in base.rglob("*"):
        if archivo.is_file():
            try:
                por_tamano[archivo.stat().st_size].append(archivo)
            except (PermissionError, OSError):
                continue

    # Paso 2 y 3: solo hashear los tamaños que tienen 2+ archivos
    por_hash = defaultdict(list)
    hasheados = 0
    for tamano, archivos in por_tamano.items():
        if len(archivos) < 2:
            continue                     # tamaño unico: no puede haber duplicado
        for archivo in archivos:
            try:
                por_hash[hash_archivo(archivo)].append(archivo)
                hasheados += 1
            except (PermissionError, OSError):
                continue

    grupos = [arch for arch in por_hash.values() if len(arch) > 1]
    return grupos, hasheados


def conservar_de(grupo, criterio):
    """Devuelve el archivo del grupo que hay que CONSERVAR, segun el criterio."""
    if criterio == "corto":
        return min(grupo, key=lambda a: len(a.name))
    if criterio == "antiguo":
        return min(grupo, key=lambda a: a.stat().st_mtime)
    if criterio == "nuevo":
        return max(grupo, key=lambda a: a.stat().st_mtime)
    return grupo[0]                      # "primero"


def main():
    args = parsear_args()
    base = Path(args.carpeta).expanduser()

    if not base.is_dir():
        print(f"No existe la carpeta: {base}")
        return

    print(f"Buscando duplicados en: {base}\n")

    grupos, hasheados = agrupar_duplicados(base)

    if not grupos:
        print(f"No se encontraron duplicados. (Se hashearon solo {hasheados} archivos.)")
        return

    espacio_recuperable = 0
    for i, grupo in enumerate(grupos, 1):
        tam = grupo[0].stat().st_size
        espacio_recuperable += tam * (len(grupo) - 1)
        conservado = conservar_de(grupo, args.conservar)
        print(f"Grupo {i} ({len(grupo)} iguales, {tam} bytes c/u):")
        for a in grupo:
            marca = "  [CONSERVAR]" if a == conservado else "  [copia]    "
            print(f"  {marca} {a}")
        print()

    print(f"{len(grupos)} grupo(s) de duplicados. "
          f"(Optimizacion: solo se hashearon {hasheados} archivos.)")
    print(f"Espacio recuperable: {espacio_recuperable} bytes "
          f"({espacio_recuperable / 1_000_000:.1f} MB)")
    print(f"Criterio para conservar: {args.conservar}")

    if args.borrar:
        print("\nSe conserva el marcado [CONSERVAR] en cada grupo y se borra el resto.")
        resp = input("¿Seguro? Escribí 'si' para confirmar: ").strip().lower()
        if resp == "si":
            borrados = 0
            for grupo in grupos:
                conservado = conservar_de(grupo, args.conservar)
                for copia in grupo:
                    if copia != conservado:
                        copia.unlink()
                        borrados += 1
            print(f"Listo. {borrados} copia(s) borrada(s).")
        else:
            print("Cancelado. No se borró nada.")


if __name__ == "__main__":
    main()
