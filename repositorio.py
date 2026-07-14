#  repositorio.py — Persistencia blindada con SQLite
#  Es el único archivo que "toca" la base de datos directamente.
#  El resto del sistema sigue usando las mismas funciones de
#  siempre (cargar_productos, guardar_productos, proximo_id),
#  así que VistaCliente.py y VistaAdmin.py NO necesitan cambios.

import sqlite3
import json
import os
import shutil
from datetime import datetime
from contextlib import contextmanager
from ClaseProducto import Producto
import sys

if getattr(sys, 'frozen', False):
    # Si el programa está compilado
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Si corre como script común de Python
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_ARCHIVO = os.path.join(BASE_DIR, "kiosco.db")
JSON_LEGACY = os.path.join(BASE_DIR, "datos.json")
CARPETA_BACKUPS = os.path.join(BASE_DIR, "backups")

MAX_BACKUPS = 10
def _conectar() -> sqlite3.Connection:
    """
    Abre una conexión con las protecciones activadas:
    - WAL: permite lecturas mientras hay una escritura en curso
      y es mucho más resistente a corrupción si se corta la luz
      o se cierra el programa a la fuerza.
    - busy_timeout: si la base está ocupada (ej. backup en curso),
      espera en vez de tirar error inmediatamente.
    - foreign_keys: por si en el futuro se agregan tablas relacionadas
      (ventas, detalle_venta, etc.).
    """
    conn = sqlite3.connect(DB_ARCHIVO, timeout=10)
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA busy_timeout = 5000;")
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def _transaccion():
    """
    Context manager: abre conexión, ejecuta, y hace commit si todo
    salió bien o rollback automático si algo falla. Así nunca queda
    la base de datos "a medio guardar".
    """
    conn = _conectar()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def _crear_esquema():
    """Crea la tabla productos si todavía no existe."""
    with _transaccion() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre    TEXT    NOT NULL,
                precio    REAL    NOT NULL CHECK(precio > 0),
                categoria TEXT    NOT NULL,
                stock     INTEGER NOT NULL CHECK(stock >= 0)
            );
        """)


def _migrar_desde_json_si_corresponde():
    """
    Si la tabla está vacía y existe un datos.json viejo, importa esos
    productos una sola vez. Las corridas siguientes no vuelven a tocar
    el JSON (la base de datos pasa a ser la única fuente de verdad).
    """
    with _conectar() as conn:
        cantidad = conn.execute("SELECT COUNT(*) FROM productos").fetchone()[0]

    if cantidad > 0 or not os.path.exists(JSON_LEGACY):
        return

    try:
        with open(JSON_LEGACY, "r", encoding="utf-8") as f:
            datos = json.load(f)

        with _transaccion() as conn:
            for p in datos.get("productos", []):
                conn.execute(
                    "INSERT INTO productos (id, nombre, precio, categoria, stock) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (p["id"], p["nombre"], p["precio"], p["categoria"], p["stock"])
                )
        print(f" Migración inicial completada desde {os.path.basename(JSON_LEGACY)}")
    except (json.JSONDecodeError, KeyError, sqlite3.Error) as e:
        print(f"No se pudo migrar {os.path.basename(JSON_LEGACY)}: {e}")


def _hacer_backup():
    """
    Copia el archivo .db actual a /backups con timestamp antes de
    cualquier escritura relevante. Conserva solo los últimos
    MAX_BACKUPS para no llenar el disco con el tiempo.
    """
    if not os.path.exists(DB_ARCHIVO):
        return

    os.makedirs(CARPETA_BACKUPS, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = os.path.join(CARPETA_BACKUPS, f"kiosco_{timestamp}.db")

    try:
        shutil.copy2(DB_ARCHIVO, destino)
    except OSError as e:
        print(f"No se pudo crear backup: {e}")
        return

    backups = sorted(
        f for f in os.listdir(CARPETA_BACKUPS)
        if f.startswith("kiosco_") and f.endswith(".db")
    )
    exceso = len(backups) - MAX_BACKUPS
    for viejo in backups[:max(exceso, 0)]:
        try:
            os.remove(os.path.join(CARPETA_BACKUPS, viejo))
        except OSError:
            pass


def verificar_integridad() -> bool:
    """
    Corre el chequeo interno de SQLite (PRAGMA integrity_check).
    Devuelve True si la base está sana, False si detecta corrupción.
    """
    try:
        with _conectar() as conn:
            resultado = conn.execute("PRAGMA integrity_check;").fetchone()[0]
        return resultado == "ok"
    except sqlite3.Error:
        return False


def restaurar_ultimo_backup() -> bool:
    """
    Restaura el backup más reciente disponible, sobreescribiendo la
    base de datos actual. Devuelve True si pudo restaurar algo.
    Pensada para usarse manualmente si inicializar() detecta corrupción.
    """
    if not os.path.exists(CARPETA_BACKUPS):
        return False

    backups = sorted(
        f for f in os.listdir(CARPETA_BACKUPS)
        if f.startswith("kiosco_") and f.endswith(".db")
    )
    if not backups:
        return False

    ultimo = os.path.join(CARPETA_BACKUPS, backups[-1])
    try:
        shutil.copy2(ultimo, DB_ARCHIVO)
        print(f" Base de datos restaurada desde {backups[-1]}")
        return True
    except OSError as e:
        print(f" No se pudo restaurar el backup: {e}")
        return False

def inicializar():
    """
    Debe llamarse una sola vez, al arrancar Main.py, antes de abrir
    cualquier ventana. Crea el esquema si no existe, migra el JSON
    viejo si corresponde, y verifica que la base no esté corrupta.

    Cubre dos niveles de corrupción distintos:
    1) Corrupción total (el archivo ni se puede abrir como SQLite):
       sqlite3 tira DatabaseError apenas se intenta conectar.
    2) Corrupción parcial (el archivo abre pero tiene páginas dañadas):
       se detecta con PRAGMA integrity_check.
    En ambos casos, si hay un backup disponible, se restaura solo.
    Si no hay backup, se avisa por consola en vez de crashear el programa.
    """
    try:
        _crear_esquema()
        _migrar_desde_json_si_corresponde()
        base_sana = verificar_integridad()
    except sqlite3.Error as e:
        print(f" La base de datos no se puede abrir ({e}).")
        base_sana = False

    if not base_sana:
        print(" ALERTA: la base de datos parece corrupta.")
        if restaurar_ultimo_backup():
            print("   Se restauró automáticamente el último backup disponible.")
            _crear_esquema()  
        else:
            print("   No hay backups disponibles para restaurar.")
            print("   Carpeta de backups:", CARPETA_BACKUPS)

# API PÚBLICA — mismas firmas que el repositorio anterior

def cargar_productos() -> list[Producto]:
    """
    Lee todos los productos desde la base de datos.
    Si hay cualquier error de lectura, devuelve lista vacía en vez
    de crashear el programa completo.
    """
    try:
        with _conectar() as conn:
            filas = conn.execute(
                "SELECT id, nombre, precio, categoria, stock "
                "FROM productos ORDER BY id"
            ).fetchall()
        return [
            Producto(
                id=f["id"], nombre=f["nombre"], precio=f["precio"],
                categoria=f["categoria"], stock=f["stock"]
            )
            for f in filas
        ]
    except sqlite3.Error as e:
        print(f" Error leyendo productos: {e}")
        return []


def guardar_productos(productos: list[Producto]):
    """
    Sincroniza la lista completa de productos con la base de datos.
    Hace un backup ANTES de escribir. Toda la operación corre dentro
    de una transacción: si algo falla a mitad de camino, se revierte
    entero y la base queda como estaba (nunca a medio guardar).
    """
    _hacer_backup()

    try:
        with _transaccion() as conn:
            conn.execute("DELETE FROM productos")
            conn.executemany(
                "INSERT INTO productos (id, nombre, precio, categoria, stock) "
                "VALUES (?, ?, ?, ?, ?)",
                [(p.id, p.nombre, p.precio, p.categoria, p.stock) for p in productos]
            )
    except sqlite3.Error as e:
        print(f" Error guardando productos, la operación se revirtió: {e}")
        raise


def proximo_id(productos: list[Producto]) -> int:
    """
    Genera el próximo ID disponible en base a la lista en memoria.
    Se mantiene por compatibilidad con VistaAdmin.py.
    """
    if not productos:
        return 1
    return max(p.id for p in productos) + 1

if __name__ == "__main__":
    inicializar()
    productos = cargar_productos()
    print(f"\nSe cargaron {len(productos)} productos:\n")
    for p in productos:
        print(f"  [{p.categoria}] {p}")