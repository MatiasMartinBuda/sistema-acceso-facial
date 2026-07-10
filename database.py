"""
Memoria persistente del sistema (Sección 6 del TP).

Implementa, sobre SQLite:
- Historial de usuarios (personas registradas, roles, lista negra)
- Decisiones anteriores / logs de acceso (Historial_Accesos)
- Resultados obtenidos (para el módulo de reportes)
- Reglas simples derivadas del historial (ej: 3 rechazos -> lista negra)
"""
import sqlite3
import datetime
from contextlib import contextmanager

import config


def _connect():
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


@contextmanager
def get_conn():
    conn = _connect()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS personas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            label_lbph INTEGER UNIQUE,        -- id numérico usado por el modelo LBPH
            dni TEXT UNIQUE,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            categoria TEXT NOT NULL,          -- administrador | propietario | inquilino | visita_frecuente
            depto TEXT,
            tipo_acceso TEXT DEFAULT 'permanente',  -- temporal | permanente | residente
            pin TEXT,                         -- código alternativo (Camino B)
            lista_negra INTEGER DEFAULT 0,
            fecha_alta TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS logs_acceso (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            persona_id INTEGER,
            dni_declarado TEXT,
            depto_destino TEXT,
            camino TEXT,               -- A | B | C
            resultado TEXT,            -- permitido | denegado | abandono
            score REAL,
            detalle TEXT,
            FOREIGN KEY(persona_id) REFERENCES personas(id)
        );
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS rechazos_visita (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            depto_destino TEXT,
            foto_path TEXT
        );
        """)


# ---------------- Personas ----------------

def siguiente_label_lbph():
    with get_conn() as conn:
        row = conn.execute("SELECT MAX(label_lbph) AS m FROM personas").fetchone()
        return 1 if row["m"] is None else row["m"] + 1


def alta_persona(dni, nombre, apellido, categoria, depto, tipo_acceso="permanente", pin=None):
    label = siguiente_label_lbph()
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO personas (label_lbph, dni, nombre, apellido, categoria, depto, tipo_acceso, pin)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (label, dni, nombre, apellido, categoria, depto, tipo_acceso, pin))
    return label


def get_persona_by_label(label):
    with get_conn() as conn:
        return conn.execute("SELECT * FROM personas WHERE label_lbph = ?", (label,)).fetchone()


def get_persona_by_pin(depto, pin):
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM personas WHERE depto = ? AND pin = ?", (depto, pin)
        ).fetchone()


def esta_en_lista_negra(label):
    with get_conn() as conn:
        row = conn.execute("SELECT lista_negra FROM personas WHERE label_lbph = ?", (label,)).fetchone()
        return bool(row and row["lista_negra"])


def marcar_lista_negra(label):
    with get_conn() as conn:
        conn.execute("UPDATE personas SET lista_negra = 1 WHERE label_lbph = ?", (label,))


def listar_personas():
    with get_conn() as conn:
        return conn.execute("SELECT * FROM personas ORDER BY apellido").fetchall()


# ---------------- Logs / auditoría ----------------

def log_evento(camino, resultado, persona_id=None, dni_declarado=None,
               depto_destino=None, score=None, detalle=""):
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO logs_acceso (persona_id, dni_declarado, depto_destino, camino, resultado, score, detalle)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (persona_id, dni_declarado, depto_destino, camino, resultado, score, detalle))


def registrar_rechazo_visita(depto_destino, foto_path=None):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO rechazos_visita (depto_destino, foto_path) VALUES (?, ?)",
            (depto_destino, foto_path)
        )


def rechazos_recientes_por_depto(depto_destino, ventana_horas=24):
    """Cuenta cuántas veces fue rechazada una visita hacia distintos deptos
    en la última ventana de tiempo (aproximación al 'rechazado 3 veces' del PDF)."""
    limite = (datetime.datetime.now() - datetime.timedelta(hours=ventana_horas)).isoformat()
    with get_conn() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS c FROM rechazos_visita WHERE timestamp >= ?",
            (limite,)
        ).fetchone()
        return row["c"]


def reporte_semanal():
    """Módulo de Reportes (Sección 6): totales de la última semana."""
    limite = (datetime.datetime.now() - datetime.timedelta(days=7)).isoformat()
    with get_conn() as conn:
        total = conn.execute(
            "SELECT COUNT(*) c FROM logs_acceso WHERE timestamp >= ?", (limite,)
        ).fetchone()["c"]
        permitidos = conn.execute(
            "SELECT COUNT(*) c FROM logs_acceso WHERE timestamp >= ? AND resultado='permitido'", (limite,)
        ).fetchone()["c"]
        denegados = conn.execute(
            "SELECT COUNT(*) c FROM logs_acceso WHERE timestamp >= ? AND resultado='denegado'", (limite,)
        ).fetchone()["c"]
        por_camino = conn.execute(
            "SELECT camino, COUNT(*) c FROM logs_acceso WHERE timestamp >= ? GROUP BY camino", (limite,)
        ).fetchall()
        return {
            "total": total,
            "permitidos": permitidos,
            "denegados": denegados,
            "por_camino": {r["camino"]: r["c"] for r in por_camino},
        }
