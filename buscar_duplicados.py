#!/usr/bin/env python3
"""
Buscador de archivos duplicados - v1

Recorre una carpeta (y sus subcarpetas) y encuentra archivos con contenido
IDENTICO, aunque tengan nombres distintos. Por defecto solo los LISTA; no
borra nada.

Como funciona: calcula el "hash" de cada archivo (una huella digital de su
contenido). Dos archivos con el mismo contenido dan el mismo hash. Comparar
hashes es rapido y confiable, no hace falta comparar byte por byte.

Uso:
    python3 buscar_duplicados.py                  # busca en ~/Descargas
    python3 buscar_duplicados.py ~/Imagenes       # en otra carpeta
    python3 buscar_duplicados.py ~/fotos --borrar # listar y OFRECER borrar
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
                   help="despues de listar, ofrece borrar las copias (deja una)")
    return p.parse_args()


def hash_archivo(ruta, bloque=65536):
    """
    Calcula el hash SHA-256 del contenido de un archivo.
    Lo lee de a bloques (64 KB) para no cargar archivos enormes enteros en RAM.
    """
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        while True:
            datos = f.read(bloque)
            if not datos:
                break
            h.update(datos)
    return h.hexdigest()


def main():
    args = parsear_args()
    base = Path(args.carpeta).expanduser()

    if not base.is_dir():
        print(f"No existe la carpeta: {base}")
        return

    print(f"Buscando duplicados en: {base}\n")

    # Agrupamos archivos por su hash. Los que caigan en el mismo grupo son copias.
    por_hash = defaultdict(list)
    for archivo in base.rglob("*"):   # rglob = recorre tambien subcarpetas
        if archivo.is_file():
            try:
                por_hash[hash_archivo(archivo)].append(archivo)
            except (PermissionError, OSError):
                # archivo que no se puede leer: lo salteamos sin cortar todo
                continue

    # Nos quedan solo los grupos con mas de un archivo (los duplicados)
    grupos = [archivos for archivos in por_hash.values() if len(archivos) > 1]

    if not grupos:
        print("No se encontraron duplicados.")
        return

    espacio_recuperable = 0
    for i, archivos in enumerate(grupos, 1):
        tam = archivos[0].stat().st_size
        copias = len(archivos) - 1          # una se conserva, el resto son copias
        espacio_recuperable += tam * copias
        print(f"Grupo {i} ({len(archivos)} iguales, {tam} bytes c/u):")
        for a in archivos:
            print(f"    {a}")
        print()

    print(f"{len(grupos)} grupo(s) de duplicados.")
    print(f"Espacio recuperable si borrás las copias: {espacio_recuperable} bytes "
          f"({espacio_recuperable / 1_000_000:.1f} MB)")

    if args.borrar:
        print("\n--borrar activado: de cada grupo se conserva el PRIMERO y se borran las copias.")
        resp = input("¿Seguro? Escribí 'si' para confirmar: ").strip().lower()
        if resp == "si":
            borrados = 0
            for archivos in grupos:
                for copia in archivos[1:]:   # salteamos el primero (el que se queda)
                    copia.unlink()
                    borrados += 1
            print(f"Listo. {borrados} copia(s) borrada(s).")
        else:
            print("Cancelado. No se borró nada.")


if __name__ == "__main__":
    main()
