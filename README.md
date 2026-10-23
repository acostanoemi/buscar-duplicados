# buscar-duplicados

Script de Python que recorre una carpeta (y sus subcarpetas) y encuentra archivos con **contenido idéntico**, aunque tengan nombres distintos. Sirve para limpiar copias repetidas y recuperar espacio.

## Solo detecta copias exactas

Compara el contenido **byte por byte** (vía hash). Solo marca archivos que son clones perfectos. **No** detecta fotos "parecidas" ni versiones de distinta calidad: esas tienen contenido distinto y el script no las toca. Por eso borrar o mover una copia nunca te hace perder calidad: son idénticas.

## Cómo funciona

Compara el contenido con el hash SHA-256 (una huella digital única): mismo contenido, mismo hash.

Para ser rápido en carpetas grandes, primero agrupa por **tamaño** (dato gratis) y solo hashea los archivos que comparten tamaño con otro. Si un tamaño es único, ese archivo no puede tener duplicado y ni se lee. Es el principio de "filtrar con lo barato antes de hacer lo caro".

## Qué hace con las copias

Por defecto **solo lista**. Para limpiar, dos modos:

- `--mover` (recomendado): manda las copias a una carpeta `_duplicados/` dentro de la carpeta analizada. Es reversible: las revisás con calma y las borrás vos cuando quieras.
- `--borrar`: las elimina definitivamente.

Ambos piden confirmación. Con `--conservar` elegís cuál copia de cada grupo se queda.

## Requisitos

Solo Python 3. No usa librerías externas.

## Uso

```bash
python3 buscar_duplicados.py                      # listar, ~/Descargas
python3 buscar_duplicados.py ~/fotos --mover      # mover copias a _duplicados/
python3 buscar_duplicados.py ~/fotos --borrar     # borrar copias
python3 buscar_duplicados.py ~/fotos --mover --conservar nuevo
```

| Opción | Qué hace |
|--------|----------|
| `carpeta` | Dónde buscar, incluye subcarpetas (default: `~/Descargas`) |
| `--mover` | Mover las copias a `_duplicados/` (reversible) |
| `--borrar` | Borrar las copias definitivamente |
| `--conservar` | Cuál copia conservar: `primero` (default), `corto`, `antiguo`, `nuevo` |

## Roadmap

- [x] v1: detectar duplicados por hash y ofrecer borrar
- [x] v2: optimizar comparando primero por tamaño
- [x] v3: elegir cuál copia conservar (`--conservar`)
- [x] v4: mover las copias a una carpeta en vez de borrarlas (`--mover`)
