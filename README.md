# Kingship

¿A qué campeón de ajedrez te pareces?

Proyecto final de Matemáticas Discretas (MAT 4021), Universidad del Norte, 2026.

Kingship es una aplicación para jugar ajedrez contra Stockfish. Al final te dice a cuál de estos cinco campeones mundiales se parece tu forma de jugar: Capablanca, Tal, Petrosian, Karpov o Carlsen.

Para esto entrenamos una red neuronal con 9.995 partidas clásicas de los cinco campeones. De cada partida sacamos 30 parámetros (porcentaje de capturas, jaques, jugadas con cada pieza, cuándo enroca, etc.). La red los agrupa en 10 nodos de estilo y al final da el porcentaje de parecido con cada campeón.

## Qué se necesita

- Python 3.10, 3.11 o 3.12
- Stockfish (el motor de ajedrez contra el que se juega)

## Instalación

1. Descargar el proyecto:

```
git clone https://github.com/llancherof-fl/kingship-chess.git
cd kingship-chess
```

2. Instalar las librerías:

```
pip install -r requirements.txt
```

Si `torch` no se instala, probar con:

```
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

3. Descargar Stockfish para Windows de https://stockfishchess.org/download/, crear una carpeta `stockfish` dentro del proyecto y poner ahí el ejecutable con este nombre:

```
kingship-chess/stockfish/stockfish-windows-x86-64-universal.exe
```

Stockfish no está en el repositorio porque es un programa aparte.

## Cómo usarlo

```
python inicio.py
```

En la pantalla de inicio se pueden ver los cinco campeones. Para jugar hay que crear una cuenta (usuario y clave), y luego se juega contra Stockfish con el nivel y el color que uno quiera. Las partidas se guardan solas en `usuarios/<tu usuario>/`.

Con el botón "Ver resultados" se ve el campeón al que más te pareces, el porcentaje con cada uno, tus 10 nodos de estilo, qué tan confiable es el resultado y tres partidas del campeón para estudiar.

Ojo: solo cuentan las partidas en las que hiciste al menos 10 jugadas. Entre más partidas juegues, más confiable es el resultado.

Si se quiere volver a entrenar la red (no es necesario, el modelo ya viene en `red_estilo.pt`):

```
python red_estilo.py
```

## Archivos

- `inicio.py`: abre la aplicación
- `campeon.py`: pantalla de cada campeón
- `usuarios.py`: cuentas y guardado de partidas
- `tablero.py`: el tablero contra Stockfish
- `resultados.py`: pantalla de resultados
- `parametros.py`: saca los 30 parámetros de una partida
- `capa1.py`: la red neuronal
- `red_estilo.py`: entrena la red; el modelo queda en `red_estilo.pt`
- `analizar_partida.py` y `analizar_jugador.py`: analizan las partidas del usuario con la red
- `base_entrenamiento.csv`: las 9.995 partidas ya convertidas a parámetros
- `entrenar.py`: primera versión del modelo, con scikit-learn
- `prueba.pgn`: partida de prueba

Las partidas de los campeones se sacaron de ChessBase (https://players.chessbase.com/en/search).

## Integrantes

Harry Kligman Cubillos, Laura Lanchero Flórez, María Tamara Zedán, Sahid Torres Colmenares y Gabriela Torres Gómez.