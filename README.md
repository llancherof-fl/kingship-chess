# Kingship ♔

**¿A qué campeón de ajedrez te pareces?**

Kingship analiza tus partidas de ajedrez y te dice a cuál de cinco campeones mundiales se parece tu estilo de juego: **Capablanca, Tal, Petrosian, Karpov o Carlsen**. Para eso usa una red neuronal entrenada con 9.995 partidas clásicas de esos campeones.

Proyecto final de **Matemáticas Discretas (MAT 4021)**, Universidad del Norte, 2026.

## ¿Cómo funciona?

```
Partida (PGN)  →  30 parámetros de estilo  →  Red neuronal  →  % de parecido con cada campeón
```

1. **Parámetros de estilo:** de cada partida se calculan 30 números a partir de las jugadas (porcentaje de capturas, de jaques, de jugadas de peón, en qué jugada enroca, si cambia damas temprano, etc.).
2. **Red neuronal:** la primera capa agrupa los parámetros en **10 nodos de estilo** (actividad, desarrollo, posición armónica, agresividad, táctica, estrategia, apertura, defensa, casillas débiles y técnica en el medio juego). Luego una capa oculta de 16 neuronas y una salida *softmax* dan el porcentaje de parecido con cada campeón.
3. **Fiabilidad:** con una sola partida el resultado es orientativo. Entre más partidas del usuario se analizan, más fiable es.
4. **Partidas recomendadas:** se muestran las 3 partidas del campeón más parecidas a las del usuario (vecinos más cercanos con distancia euclidiana).

## Requisitos

- **Python 3.10 a 3.12** (con `tkinter`, que viene incluido en la instalación normal de Python para Windows).
- **Stockfish**, el motor de ajedrez contra el que se juega.

## Instalación

**1. Clonar el repositorio**

```
git clone https://github.com/llancherof-fl/kingship-chess.git
cd kingship-chess
```

**2. Instalar las librerías**

```
pip install -r requirements.txt
```

Si `torch` da error al instalarse, usar:

```
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

**3. Descargar Stockfish**

1. Descargarlo de <https://stockfishchess.org/download/> (versión para Windows).
2. Crear una carpeta llamada `stockfish` dentro del proyecto.
3. Poner allí el ejecutable con este nombre exacto: `stockfish-windows-x86-64-universal.exe`

Debe quedar así: `kingship-chess/stockfish/stockfish-windows-x86-64-universal.exe`

Stockfish no está en el repositorio porque es un programa aparte (está en el `.gitignore`).

## Uso

```
python inicio.py
```

Se abre la aplicación, y todas las pantallas se muestran en la misma ventana:

1. **Inicio:** tarjetas con los cinco campeones. Al hacer clic en una se ve su estilo y datos curiosos.
2. **Cuenta:** al darle *Jugar*, se inicia sesión o se crea una cuenta con usuario y clave. Las partidas de cada usuario se guardan en `usuarios/<usuario>/`.
3. **Tablero:** partida contra Stockfish, con 5 niveles (de Principiante a GM) y opción de jugar con blancas o negras. Al terminar, la partida se guarda en PGN.
4. **Resultados:** con el botón *Ver resultados* se ve el campeón más parecido, el % con cada campeón, los 10 nodos de estilo, la fiabilidad y las 3 partidas recomendadas.

> Solo se analizan las partidas en las que el usuario hizo **al menos 10 jugadas**.

### Analizar una partida sin la interfaz (opcional)

```
python analizar_partida.py
```

Analiza `prueba.pgn` (la "Partida de la Ópera" de Morphy, 1858) y muestra en la terminal el % de parecido con cada campeón y los 10 nodos de estilo.

### Volver a entrenar la red (opcional)

El modelo ya entrenado está en `red_estilo.pt`, así que no hace falta entrenarlo para usar la aplicación. Para reentrenarlo:

```
python red_estilo.py
```

Imprime la exactitud, la matriz de confusión, el acierto según el número de partidas y el perfil medio de cada campeón, y guarda el modelo nuevo en `red_estilo.pt`.

### Regenerar la base de entrenamiento (opcional)

```
python parametros.py base.pgn base_entrenamiento.csv
```

Donde `base.pgn` contiene las partidas de los cinco campeones. Se descartan automáticamente las partidas no clásicas.

## Estructura del proyecto

| Archivo | Qué hace |
|---|---|
| `inicio.py` | Abre la aplicación: pantalla de inicio, cuentas y navegación entre pantallas |
| `campeon.py` | Pantalla de cada campeón (estilo y datos curiosos) |
| `usuarios.py` | Cuentas de usuario y guardado de partidas |
| `tablero.py` | Tablero para jugar contra Stockfish |
| `resultados.py` | Pantalla de resultados |
| `analizar_partida.py` | Carga el modelo y analiza una partida |
| `analizar_jugador.py` | Analiza todas las partidas de un usuario y calcula la fiabilidad |
| `parametros.py` | Extrae los 30 parámetros de estilo de un archivo PGN |
| `capa1.py` | Definición de la red neuronal (10 nodos de estilo + capa oculta + softmax) |
| `red_estilo.py` | Entrena y evalúa la red |
| `red_estilo.pt` | Modelo ya entrenado |
| `base_entrenamiento.csv` | 9.995 partidas de los cinco campeones convertidas a parámetros |
| `prueba.pgn` | Partida de prueba |
| `entrenar.py` | Versión inicial del modelo con scikit-learn, usada como punto de comparación |
| `piezas/`, `imagenes/` | Imágenes de las piezas, los campeones y la interfaz |

## Datos

| Campeón | Partidas |
|---|---|
| Tal | 2.744 |
| Karpov | 2.334 |
| Petrosian | 2.212 |
| Carlsen | 2.047 |
| Capablanca | 658 |
| **Total** | **9.995** |

Solo partidas clásicas, de 1901 a 2024. Fuente: [ChessBase Players](https://players.chessbase.com/en/search).

Las imágenes de las piezas son las de [Lichess](https://github.com/lichess-org/lila) (licencia libre).

## Integrantes

- Harry Kligman Cubillos
- Laura Lanchero Flórez
- María Tamara Zedán
- Sahid Torres Colmenares
- Gabriela Torres Gómez
