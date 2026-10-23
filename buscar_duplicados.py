#!/usr/bin/env python3
"""
Buscador de archivos duplicados - v4

Recorre una carpeta (y sus subcarpetas) y encuentra archivos con contenido
IDENTICO, aunque tengan nombres distintos. Por defecto solo los LISTA.

IMPORTANTE: solo detecta copias EXACTAS (byte por byte). No detecta fotos
"parecidas" ni versiones de distinta calidad: esas tienen contenido distinto
y el script no las toca. Borrar o mover una copia exacta nunca te hace perder
calidad, porque son clones identicos.

Como funciona:
  1. Agrupa por TAMAÑO (dato gratis): si un tamaño es unico, no puede tener
     duplicado, y no se hashea. Asi se evita leer casi todos los archivos.
  2. Hashea solo los que comparten tamaño y agrupa por hash.

Al limpiar, podés:
  --mover   : manda las copias a una carpeta (reversible, recomendado)
  --borrar  : las borra definitivamente (pide confirmacion)
Y con --conservar elegís cual copia de cada grupo se queda.

Uso:
    python3 buscar_duplicados.py                      # listar, ~/Descargas
    python3 buscar_duplicados.py ~/fotos --mover      # mover copias a _duplicados/
    python3 buscar_duplicados.py ~/fotos --borrar     # borrar copias
    python3 buscar_duplicados.py ~/fotos --mover --conservar nuevo
"""

import shutil
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
    p.add_argument("--mover", action="store_true",
                   help="mover las copias a una carpeta _duplicados/ (reversible)")
    p.add_argument("--borrar", action="store_true",
                   help="borrar las copias definitivamente (pide confirmacion)")
    p.add_argument("--conservar", choices=["primero", "corto", "antiguo", "nuevo"],
                   default="primero",
                   help="cual copia conservar de cada grupo "
                        "(primero/corto/antiguo/nuevo). Default: primero")
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


def agrupar_duplicados(base, carpeta_duplicados):
    """
    Devuelve (grupos, hasheados). Cada grupo es una lista de archivos identicos.
    Optimizacion: solo hashea archivos que comparten tamaño con otro.
    Ignora lo que ya este dentro de la carpeta _duplicados/ (de corridas previas).
    """
    por_tamano = defaultdict(list)
    for archivo in base.rglob("*"):
        if not archivo.is_file():
            continue
        # No re-procesar lo que ya movimos antes
        if carpeta_duplicados in archivo.parents:
            continue
        try:
            por_tamano[archivo.stat().st_size].append(archivo)
        except (PermissionError, OSError):
            continue

    por_hash = defaultdict(list)
    hasheados = 0
    for archivos in por_tamano.values():
        if len(archivos) < 2:
            continue
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
    return grupo[0]


def destino_sin_pisar(carpeta, nombre):
    """Si en el destino ya hay un archivo con ese nombre, le agrega un numero."""
    if not (carpeta / nombre).exists():
        return carpeta / nombre
    base, punto, ext = nombre.rpartition(".")
    if not punto:
        base, ext = nombre, ""
    n = 1
    while True:
        candidato = f"{base}_{n}.{ext}" if ext else f"{base}_{n}"
        if not (carpeta / candidato).exists():
            return carpeta / candidato
        n += 1


def main():
    args = parsear_args()
    base = Path(args.carpeta).expanduser()

    if not base.is_dir():
        print(f"No existe la carpeta: {base}")
        return

    if args.mover and args.borrar:
        print("Elegí una sola: --mover o --borrar, no las dos.")
        return

    carpeta_duplicados = base / "_duplicados"

    print(f"Buscando duplicados en: {base}\n")
    grupos, hasheados = agrupar_duplicados(base, carpeta_duplicados)

    if not grupos:
        print(f"No se encontraron duplicados. (Se hashearon solo {hasheados} archivos.)")
        return

    espacio = 0
    for i, grupo in enumerate(grupos, 1):
        tam = grupo[0].stat().st_size
        espacio += tam * (len(grupo) - 1)
        conservado = conservar_de(grupo, args.conservar)
        print(f"Grupo {i} ({len(grupo)} iguales, {tam} bytes c/u):")
        for a in grupo:
            marca = "[CONSERVAR]" if a == conservado else "[copia]    "
            print(f"  {marca} {a}")
        print()

    print(f"{len(grupos)} grupo(s) de duplicados. "
          f"(Optimizacion: solo se hashearon {hasheados} archivos.)")
    print(f"Espacio recuperable: {espacio} bytes ({espacio / 1_000_000:.1f} MB)")
    print(f"Criterio para conservar: {args.conservar}")

    # --- Acciones ---
    if not (args.mover or args.borrar):
        print("\n(Solo listado. Usá --mover para apartarlas o --borrar para eliminarlas.)")
        return

    if args.mover:
        print(f"\nSe moverán las copias a: {carpeta_duplicados}")
        print("(Quedan ahí para que las revises; después las borrás vos cuando quieras.)")
        resp = input("¿Seguro? Escribí 'si' para confirmar: ").strip().lower()
        if resp != "si":
            print("Cancelado. No se movió nada.")
            return
        carpeta_duplicados.mkdir(exist_ok=True)
        movidos = 0
        for grupo in grupos:
            conservado = conservar_de(grupo, args.conservar)
            for copia in grupo:
                if copia != conservado:
                    destino = destino_sin_pisar(carpeta_duplicados, copia.name)
                    shutil.move(str(copia), str(destino))
                    movidos += 1
        print(f"Listo. {movidos} copia(s) movida(s) a {carpeta_duplicados}")
        return

    if args.borrar:
        print("\nSe borrará (definitivo) el resto de cada grupo, dejando el [CONSERVAR].")
        resp = input("¿Seguro? Escribí 'si' para confirmar: ").strip().lower()
        if resp != "si":
            print("Cancelado. No se borró nada.")
            return
        borrados = 0
        for grupo in grupos:
            conservado = conservar_de(grupo, args.conservar)
            for copia in grupo:
                if copia != conservado:
                    copia.unlink()
                    borrados += 1
        print(f"Listo. {borrados} copia(s) borrada(s).")


if __name__ == "__main__":
    main()
