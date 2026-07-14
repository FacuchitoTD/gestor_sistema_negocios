#  repositorio.py — Persistencia blindada con SQLite
#  Es el único archivo que "toca" la base de datos directamente.

import sqlite3
import json
import os
import shutil
from datetime import datetime
from contextlib import contextmanager
from ClaseProducto import Producto

import sys
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_ARCHIVO      = os.path.join(BASE_DIR, "kiosco.db")
JSON_LEGACY     = os.path.join(BASE_DIR, "datos.json")
CARPETA_BACKUPS = os.path.join(BASE_DIR, "backups")

MAX_BACKUPS = 10

def _conectar() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_ARCHIVO, timeout=10)
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA busy_timeout = 5000;")
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def _transaccion():
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
    """Crea la tabla productos si todavía no existe (instalaciones nuevas)."""
    with _transaccion() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre        TEXT    NOT NULL,
                precio        REAL    NOT NULL CHECK(precio > 0),
                categoria     TEXT    NOT NULL,
                stock         INTEGER NOT NULL CHECK(stock >= 0),
                codigo_barras TEXT
            );
        """)


def _migrar_columna_codigo_barras():
    """
    Si la base de datos ya existía de antes (sin la columna
    codigo_barras), se la agrega ahora sin tocar los datos existentes.
    CREATE TABLE IF NOT EXISTS no alcanza para esto: solo crea la tabla
    si no existe, no le agrega columnas nuevas a una tabla vieja.
    """
    with _transaccion() as conn:
        columnas = [fila["name"] for fila in conn.execute("PRAGMA table_info(productos)")]
        if "codigo_barras" not in columnas:
            conn.execute("ALTER TABLE productos ADD COLUMN codigo_barras TEXT")
            print("Migración: columna 'codigo_barras' agregada a productos existentes.")

        conn.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_codigo_barras_unico
            ON productos(codigo_barras)
            WHERE codigo_barras IS NOT NULL AND codigo_barras != ''
        """)


def _migrar_desde_json_si_corresponde():
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
                    "INSERT INTO productos (id, nombre, precio, categoria, stock, codigo_barras) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (p["id"], p["nombre"], p["precio"], p["categoria"], p["stock"],
                    p.get("codigo_barras"))
                )
        print(f"Migración inicial completada desde {os.path.basename(JSON_LEGACY)}")
    except (json.JSONDecodeError, KeyError, sqlite3.Error) as e:
        print(f"No se pudo migrar {os.path.basename(JSON_LEGACY)}: {e}")

def _hacer_backup():
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
    try:
        with _conectar() as conn:
            resultado = conn.execute("PRAGMA integrity_check;").fetchone()[0]
        return resultado == "ok"
    except sqlite3.Error:
        return False


def restaurar_ultimo_backup() -> bool:
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
        print(f"Base de datos restaurada desde {backups[-1]}")
        return True
    except OSError as e:
        print(f"No se pudo restaurar el backup: {e}")
        return False

def inicializar():
    try:
        _crear_esquema()
        _migrar_columna_codigo_barras()
        _migrar_desde_json_si_corresponde()
        base_sana = verificar_integridad()
    except sqlite3.Error as e:
        print(f"La base de datos no se puede abrir ({e}).")
        base_sana = False

    if not base_sana:
        print("ALERTA: la base de datos parece corrupta.")
        if restaurar_ultimo_backup():
            print("   Se restauró automáticamente el último backup disponible.")
            _crear_esquema()
            _migrar_columna_codigo_barras()
        else:
            print("   No hay backups disponibles para restaurar.")
            print("   Carpeta de backups:", CARPETA_BACKUPS)


def cargar_productos() -> list[Producto]:
    try:
        with _conectar() as conn:
            filas = conn.execute(
                "SELECT id, nombre, precio, categoria, stock, codigo_barras "
                "FROM productos ORDER BY id"
            ).fetchall()
        return [
            Producto(
                id=f["id"], nombre=f["nombre"], precio=f["precio"],
                categoria=f["categoria"], stock=f["stock"],
                codigo_barras=f["codigo_barras"]
            )
            for f in filas
        ]
    except sqlite3.Error as e:
        print(f"Error leyendo productos: {e}")
        return []


def guardar_productos(productos: list[Producto]):
    """
    Sincroniza la lista completa de productos con la base de datos.
    Lanza sqlite3.IntegrityError si dos productos quedaron con el
    mismo código de barras (el índice único lo detecta) — quien
    llame a esta función debe capturarlo y avisar al usuario.
    """
    _hacer_backup()

    try:
        with _transaccion() as conn:
            conn.execute("DELETE FROM productos")
            conn.executemany(
                "INSERT INTO productos (id, nombre, precio, categoria, stock, codigo_barras) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                [(p.id, p.nombre, p.precio, p.categoria, p.stock,
                p.codigo_barras or None) for p in productos]
            )
    except sqlite3.Error as e:
        print(f"Error guardando productos, la operación se revirtió: {e}")
        raise


def proximo_id(productos: list[Producto]) -> int:
    if not productos:
        return 1
    return max(p.id for p in productos) + 1

if __name__ == "__main__":
    inicializar()
    productos = cargar_productos()
    print(f"\nSe cargaron {len(productos)} productos:\n")
    for p in productos:
        print(f"  [{p.categoria}] {p} — código: {p.codigo_barras or '(sin código)'}")