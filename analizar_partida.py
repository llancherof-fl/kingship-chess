import numpy as np
import torch

from capa1 import DIMENSIONES, RedEstilo
from parametros import leer_partidas, parametros


# CARGAR EL MODELO
modelo = torch.load("red_estilo.pt", map_location="cpu", weights_only=False)
columnas = modelo["columnas"]
campeones = modelo["clases"]

red = RedEstilo(columnas, len(campeones))
red.load_state_dict(modelo["estado"])
red.eval()


# ANALIZAR UNA PARTIDA
def analizar_partida(ruta_pgn, color=0):
    # color = 0 si el usuario jugo con blancas, 1 si jugo con negras

    # leer la partida y sacar los 30 parametros
    cabecera, jugadas = next(leer_partidas(ruta_pgn))
    datos = parametros(jugadas, color)
    if datos is None:
        return None  # la partida tiene menos de 10 jugadas

    # escalar los datos igual que en el entrenamiento
    x = np.array([datos[c] for c in columnas])
    x = (x - np.array(modelo["media"])) / np.array(modelo["escala"])
    x = torch.tensor(x, dtype=torch.float32).reshape(1, -1)

    # pasar los datos por la red
    with torch.no_grad():
        prob = torch.softmax(red(x), dim=1)[0]
        perfil = red.perfil(x)[0]

    # porcentaje de parecido con cada campeon
    resultado = {}
    for i in range(len(campeones)):
        resultado[campeones[i]] = round(prob[i].item() * 100, 1)

    # porcentaje de cada nodo de estilo
    estilo = {}
    nombres = list(DIMENSIONES.keys())
    for i in range(len(nombres)):
        estilo[nombres[i]] = round(perfil[i].item() * 100)

    return resultado, estilo, x[0].numpy()


# PRUEBA
if __name__ == "__main__":
    resultado, estilo, x = analizar_partida("prueba.pgn")
    print("Parecido con cada campeon:", resultado)
    print("Perfil de estilo:", estilo)
