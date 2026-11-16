"""Cuentas de usuario y partidas guardadas (PGN). Todo local y sin librerías extra.
Estructura:  usuarios/usuarios.json (claves con hash)  y  usuarios/<usuario>/partida_*.pgn"""
import csv
import datetime
import hashlib
import hmac
import json
import os
import re
import secrets

from parametros import COLUMNAS, leer_partidas, parametros

CARPETA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "usuarios")
ARCHIVO = os.path.join(CARPETA, "usuarios.json")


def _cargar():
    if not os.path.exists(ARCHIVO):
        return {}
    with open(ARCHIVO, encoding="utf-8") as f:
        return json.load(f)


def _hash(clave, sal):
    return hashlib.pbkdf2_hmac("sha256", clave.encode("utf-8"), bytes.fromhex(sal), 200_000).hex()


def registrar(nombre, clave):
    """Devuelve (True, nombre) o (False, mensaje de error)."""
    nombre = nombre.strip()
    if not re.fullmatch(r"\w{3,20}", nombre) or nombre.lower() == "stockfish":
        return False, "Usuario de 3 a 20 letras, números o _ (y distinto de Stockfish)"
    if len(clave) < 4:
        return False, "La clave debe tener al menos 4 caracteres"
    datos = _cargar()
    if nombre.lower() in datos:
        return False, "Ese usuario ya existe"
    sal = secrets.token_hex(16)
    datos[nombre.lower()] = {"nombre": nombre, "sal": sal, "hash": _hash(clave, sal)}
    os.makedirs(carpeta(nombre), exist_ok=True)
    with open(ARCHIVO, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=2)
    return True, nombre


def entrar(nombre, clave):
    u = _cargar().get(nombre.strip().lower())
    if not u or not hmac.compare_digest(u["hash"], _hash(clave, u["sal"])):
        return False, "Usuario o clave incorrectos"
    return True, u["nombre"]


def carpeta(nombre):
    return os.path.join(CARPETA, nombre.lower())


def guardar_pgn(nombre, pgn):
    os.makedirs(carpeta(nombre), exist_ok=True)
    ruta = os.path.join(carpeta(nombre), datetime.datetime.now().strftime("partida_%Y%m%d_%H%M%S.pgn"))
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(pgn.strip() + "\n")
    generar_csv(nombre)                 # el CSV siempre queda al día con las partidas guardadas
    return ruta


def generar_csv(nombre):
    """Crea usuarios/<usuario>/partidas.csv: una fila por partida guardada, con las mismas columnas
    que base_entrenamiento.csv (listo para analizar_jugador.py). Devuelve la ruta del CSV."""
    clave = nombre.lower()
    filas = []
    for ruta in listar_partidas(nombre):
        for cab, jugadas in leer_partidas(ruta):
            w, b = cab.get("White", ""), cab.get("Black", "")
            color = 0 if w.lower() == clave else 1 if b.lower() == clave else None
            if color is None:
                continue
            fila = parametros(jugadas, color)
            if fila is None:             # el usuario hizo menos de 10 jugadas
                continue
            fila.update(campeon=nombre, anio=cab.get("Date", "")[:4],
                        partida=f"{w} - {b}, {cab.get('Event', '')} {cab.get('Date', '')[:4]}")
            filas.append(fila)
    ruta_csv = os.path.join(carpeta(nombre), "partidas.csv")
    with open(ruta_csv, "w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=["campeon", "partida", "anio"] + COLUMNAS)
        escritor.writeheader()
        escritor.writerows(filas)
    return ruta_csv


def listar_partidas(nombre):
    c = carpeta(nombre)
    return sorted(os.path.join(c, f) for f in os.listdir(c) if f.endswith(".pgn")) if os.path.isdir(c) else []
