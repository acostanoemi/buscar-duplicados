# buscar-duplicados

Script de Python que recorre una carpeta (y sus subcarpetas) y encuentra archivos con **contenido idéntico**, aunque tengan nombres distintos. Sirve para limpiar copias repetidas y recuperar espacio.

## Cómo funciona

Compara el **contenido**, no el nombre, usando el hash SHA-256 (una huella digital única del contenido): dos archivos con el mismo contenido dan el mismo hash.

Para que sea rápido en carpetas grandes, primero agrupa por **tamaño** (dato gratis que el sistema ya conoce) y solo hashea los archivos que comparten tamaño con otro. Si un tamaño es único, ese archivo no puede tener un duplicado, así que ni se lee. De esa forma evita hashear casi todos los archivos. Es el principio de "filtrar con lo barato antes de hacer lo caro".

## Seguridad

- Por defecto **solo lista**, no borra nada.
- Con `--borrar`, conserva una copia de cada grupo y borra el resto, pero **pide confirmación** antes.
- Con `--conservar` elegís cuál copia se queda (ver abajo).
- El borrado es definitivo (no va a la papelera). Revisá la lista antes de confirmar.

## Requisitos

Solo Python 3. No usa librerías externas (`hashlib` viene con Python).

## Uso

```bash
python3 buscar_duplicados.py                      # busca en ~/Descargas
python3 buscar_duplicados.py ~/Imagenes           # en otra carpeta
python3 buscar_duplicados.py ~/fotos --borrar     # listar y ofrecer borrar
python3 buscar_duplicados.py ~/fotos --borrar --conservar antiguo
```

| Opción | Qué hace |
|--------|----------|
| `carpeta` | Dónde buscar, incluye subcarpetas (default: `~/Descargas`) |
| `--borrar` | Tras listar, ofrece borrar las copias (pide confirmación) |
| `--conservar` | Cuál copia conservar de cada grupo: `primero` (default), `corto` (nombre más corto), `antiguo` (más viejo), `nuevo` (más reciente) |

## Roadmap

- [x] v1: detectar duplicados por hash y ofrecer borrar
- [x] v2: optimizar comparando primero por tamaño (hashear solo los que coinciden)
- [x] v3: elegir cuál copia conservar (`--conservar`)
- [ ] v4: mover las copias a una carpeta en vez de borrarlas
