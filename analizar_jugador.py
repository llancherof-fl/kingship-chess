"""
Analiza el estilo de un jugador con el modelo entrenado (red_estilo.pt).

Uso:  python analizar_jugador.py partidas_jugador.csv

El CSV debe tener las MISMAS columnas que base_entrenamiento.csv (una fila por partida
del jugador; no hace falta 'campeon', 'partida' ni 'anio').

Funciona con 1 partida o con muchas. Cuantas menos partidas, menos fiable es el resultado,
y el programa lo avisa usando el acierto medido durante el entrenamiento.
"""
import os
import sys

import numpy as np
import pandas as pd
import torch

from capa1 import DIMENSIONES, RedEstilo

RUTA_MODELO = "red_estilo.pt"


def nivel_fiabilidad(n_partidas, fiabilidad):
    """Busca el acierto medido con la ventana más cercana (sin pasarse) a n_partidas."""
    ks = sorted(fiabilidad)
    k = max([x for x in ks if x <= n_partidas], default=ks[0])
    acierto = fiabilidad[k]

    if acierto < 0.50:
        etiqueta = "POCO FIABLE"
    elif acierto < 0.75:
        etiqueta = "FIABILIDAD MEDIA"
    else:
        etiqueta = "FIABLE"
    return etiqueta, acierto, k


def barra(valor, ancho=20):
    llenos = int(round(valor * ancho))
    return "█" * llenos + "·" * (ancho - llenos)

def analizar_archivo(ruta):
    if not os.path.exists(ruta):
        print("No se encuentra el archivo:", ruta)
        return

    modelo = torch.load(RUTA_MODELO, map_location="cpu")
    columnas = modelo["columnas"]
    clases = modelo["clases"]
    fiabilidad = modelo["fiabilidad"]


    d = pd.read_csv(ruta)
    
    faltan = [c for c in columnas if c not in d.columns]
    if faltan:
        print("Faltan estas columnas en el CSV:", faltan)
        return
    d = d.dropna(subset=columnas)
    n = len(d)
    if n == 0:
        print("El CSV no tiene partidas válidas.")
        return
    
    # mismo escalado que en el entrenamiento
    X = (d[columnas].values - np.array(modelo["media"])) / np.array(modelo["escala"])
    X = torch.tensor(X, dtype=torch.float32)
    
    red = RedEstilo(columnas, len(clases))
    red.load_state_dict(modelo["estado"])
    red.eval()
    
    with torch.no_grad():
        P = torch.softmax(red(X), dim=1).numpy()      # probabilidades por partida
        perfil = red.perfil(X).numpy()                # 10 nodos por partida
    
    prob = P.mean(axis=0)                             # resultado conjunto
    perfil_medio = perfil.mean(axis=0)
    
    etiqueta, acierto, k = nivel_fiabilidad(n, fiabilidad)
    X = (d[columnas].values - np.array(modelo["media"])) / np.array(modelo["escala"])
    x_medio = X.mean(axis=0)                 # <-- nuevo
    X = torch.tensor(X, dtype=torch.float32)

    return {
        "partidas": n,
        "etiqueta": etiqueta,
        "acierto": acierto,
        "ventana": k,
        "campeones": clases,
        "probabilidades": prob,
        "perfil": perfil_medio,
        "x": x_medio
    }


def main():
    if len(sys.argv) < 2:
        print("Uso: python analizar_jugador.py partidas_jugador.csv")
        return

    modelo = torch.load(RUTA_MODELO, map_location="cpu")
    columnas = modelo["columnas"]
    clases = modelo["clases"]
    fiabilidad = modelo["fiabilidad"]

    d = pd.read_csv(sys.argv[1])
    faltan = [c for c in columnas if c not in d.columns]
    if faltan:
        print("Faltan estas columnas en el CSV:", faltan)
        return
    d = d.dropna(subset=columnas)
    n = len(d)
    if n == 0:
        print("El CSV no tiene partidas válidas.")
        return

    # mismo escalado que en el entrenamiento
    X = (d[columnas].values - np.array(modelo["media"])) / np.array(modelo["escala"])
    X = torch.tensor(X, dtype=torch.float32)

    red = RedEstilo(columnas, len(clases))
    red.load_state_dict(modelo["estado"])
    red.eval()

    with torch.no_grad():
        P = torch.softmax(red(X), dim=1).numpy()      # probabilidades por partida
        perfil = red.perfil(X).numpy()                # 10 nodos por partida

    prob = P.mean(axis=0)                             # resultado conjunto
    perfil_medio = perfil.mean(axis=0)

    etiqueta, acierto, k = nivel_fiabilidad(n, fiabilidad)

    # ---------- resultado
    print("=" * 60)
    print(f"Partidas analizadas: {n}")
    print(f"Fiabilidad: {etiqueta}")
    print(f"  En las pruebas, con {k} partida(s) la red acertó el {acierto * 100:.0f} % de las veces.")
    if n < 5:
        print("  Con tan pocas partidas el resultado es solo orientativo.")
    print("=" * 60)

    print("\nParecido con cada campeón:")
    for i in np.argsort(-prob):
        print(f"  {clases[i]:12s} {prob[i] * 100:5.1f} %  {barra(prob[i])}")

    print("\nPerfil de estilo (0 a 1):")
    for nombre, v in zip(DIMENSIONES.keys(), perfil_medio):
        print(f"  {nombre:18s} {v:4.2f}  {barra(v)}")

    if n <= 5:
        print("\nPartida por partida:")
        for j in range(n):
            top = np.argsort(-P[j])[:2]
            print(f"  Partida {j + 1}: {clases[top[0]]} {P[j][top[0]] * 100:.0f} %, "
                  f"{clases[top[1]]} {P[j][top[1]] * 100:.0f} %")


if __name__ == "__main__":
    main()
