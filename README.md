# buscar-duplicados

Script de Python que recorre una carpeta (y sus subcarpetas) y encuentra archivos con **contenido idéntico**, aunque tengan nombres distintos. Sirve para limpiar copias repetidas y recuperar espacio.

## Cómo funciona

Compara el **contenido**, no el nombre. Por cada archivo calcula su hash SHA-256 (una huella digital única de su contenido); dos archivos con el mismo contenido dan el mismo hash. Agrupa por hash y los grupos con más de un archivo son duplicados. Es rápido y confiable: no compara archivos byte por byte entre sí.

## Seguridad

- Por defecto **solo lista**, no borra nada.
- Con `--borrar`, de cada grupo conserva uno y borra las copias, pero **pide confirmación** antes.
- El borrado es definitivo (no va a la papelera). Revisá la lista antes de confirmar.

## Requisitos

Solo Python 3. No usa librerías externas (`hashlib` viene con Python).

## Uso

```bash
python3 buscar_duplicados.py                  # busca en ~/Descargas
python3 buscar_duplicados.py ~/Imagenes       # en otra carpeta
python3 buscar_duplicados.py ~/fotos --borrar # listar y ofrecer borrar
```

| Opción | Qué hace |
|--------|----------|
| `carpeta` | Dónde buscar, incluye subcarpetas (default: `~/Descargas`) |
| `--borrar` | Tras listar, ofrece borrar las copias (deja una, pide confirmación) |

## Roadmap

- [x] v1: detectar duplicados por hash y ofrecer borrar
- [ ] v2: optimizar comparando primero por tamaño (hashear solo los que coinciden)
- [ ] v3: elegir cuál copia conservar en vez de quedarse siempre con la primera
