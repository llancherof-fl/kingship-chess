import os
import tkinter as tk
import chess
import chess.engine

try:
    from PIL import Image, ImageTk
    PILLOW_OK = True
except ImportError:
    PILLOW_OK = False


STOCKFISH_PATH = os.path.join(os.path.dirname(__file__), "stockfish", "stockfish-windows-x86-64-universal.exe")

CARPETA_PIEZAS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "piezas")


LINEAS = 5          
TIEMPO_ANALISIS = 0.4 

#Configuración para elegir niveles de juego
NIVELES = {
    "Principiante": (0, 0.1),
    "Fácil": (4, 0.2),
    "Intermedio": (9, 0.4),
    "Avanzado": (15, 0.6),
    "GM": (20, 1.0),
}


#Config del tablero

FONDO = "#282828"
CLARA = "#EEEED2"
OSCURA = "#8B5696"
SELECCION = "#F6F669"
ULTIMA = "#BACA44"
JAQUE = "#E5534B"


board = chess.Board()
engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
selected_square = None



#Cargar piezas (piezas propias de lichess en carpeta piezas)
imagenes_originales = {}
imagenes_cache = {}
cache_tamano = 0

if PILLOW_OK:
    for color in "wb":
        for tipo in "KQRBNP":
            nombre = color + tipo
            ruta = os.path.join(CARPETA_PIEZAS, nombre + ".png")
            if os.path.exists(ruta):
                imagenes_originales[nombre] = Image.open(ruta).convert("RGBA")

USAR_IMAGENES = len(imagenes_originales) == 12



def obtener_imagen(piece, tamano):

    global cache_tamano

    if tamano != cache_tamano:
        imagenes_cache.clear()
        cache_tamano = tamano

    nombre = ("w" if piece.color == chess.WHITE else "b") + piece.symbol().upper()

    if nombre not in imagenes_cache:
        imagen = imagenes_originales[nombre].resize((tamano, tamano), Image.LANCZOS)
        imagenes_cache[nombre] = ImageTk.PhotoImage(imagen)

    return imagenes_cache[nombre]


root = tk.Tk()
root.title("Entrenador de Ajedrez")
root.geometry("1100x700")
root.minsize(800, 500)
root.configure(bg=FONDO)

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)



left = tk.Frame(root, bg=FONDO)
left.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
left.columnconfigure(0, weight=1)
left.rowconfigure(1, weight=1)

status = tk.Label(left, text="Tu turno de jugar - Blancas", font=("Arial", 16),
                  bg=FONDO, fg="white")
status.grid(row=0, column=0, pady=10)

canvas = tk.Canvas(left, bg=FONDO, highlightthickness=0)
canvas.grid(row=1, column=0, sticky="nsew")

controles = tk.Frame(left, bg=FONDO)
controles.grid(row=2, column=0, pady=10)


right = tk.Frame(root, bg="#1e1e1e", width=380)
right.grid(row=0, column=1, sticky="ns", padx=(0, 10), pady=10)
right.pack_propagate(False)
right.grid_propagate(False)

titulo = tk.Label(right, text="Análisis del módulo", font=("Arial", 14, "bold"),
                  bg="#510043", fg="white")
titulo.pack(pady=10)

analysis_text = tk.Text(right, bg="#1e1e1e", fg="white", font=("Consolas", 11),
                        wrap="word", relief="flat", state="disabled")
analysis_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))




#Aquí es responsive 
def medidas():
    ancho = canvas.winfo_width()
    alto = canvas.winfo_height()
    margen = 20
    lado = (min(ancho, alto) - 2 * margen) / 8
    x0 = (ancho - 8 * lado) / 2
    y0 = (alto - 8 * lado) / 2
    return lado, x0, y0

def update_board():

    canvas.delete("all")
    lado, x0, y0 = medidas()

    if lado <= 0:
        return

    ultimo = board.peek() if board.move_stack else None
    rey_jaque = board.king(board.turn) if board.is_check() else None

    for square in chess.SQUARES:

        col = chess.square_file(square)
        row = 7 - chess.square_rank(square)

        x = x0 + col * lado
        y = y0 + row * lado

        color = CLARA if (row + col) % 2 == 0 else OSCURA

        if ultimo and square in (ultimo.from_square, ultimo.to_square):
            color = ULTIMA
        if square == selected_square:
            color = SELECCION
        if square == rey_jaque:
            color = JAQUE

        canvas.create_rectangle(x, y, x + lado, y + lado, fill=color, outline="")

        # puntos en las casillas a las que puede moverse la pieza seleccionada
        if selected_square is not None:
            move = chess.Move(selected_square, square)
            move_promo = chess.Move(selected_square, square, promotion=chess.QUEEN)

            if move in board.legal_moves or move_promo in board.legal_moves:
                r = lado * 0.15
                canvas.create_oval(x + lado / 2 - r, y + lado / 2 - r,
                                   x + lado / 2 + r, y + lado / 2 + r,
                                   fill="#5a7d3a", outline="")

        piece = board.piece_at(square)

        if piece:
            if USAR_IMAGENES:
                canvas.create_image(
                    x + lado / 2,
                    y + lado / 2,
                    image=obtener_imagen(piece, int(lado * 0.95))
                )
            else:
                canvas.create_text(
                    x + lado / 2,
                    y + lado / 2,
                    text=piece.unicode_symbol(),
                    font=("Segoe UI Symbol", int(lado * 0.7)),
                    fill="black"
                )

    # Para ver las coordenadas
    for i in range(8):
        canvas.create_text(x0 + i * lado + lado / 2, y0 + 8 * lado + 10,
                           text="abcdefgh"[i], fill="white")
        canvas.create_text(x0 - 10, y0 + i * lado + lado / 2,
                           text=str(8 - i), fill="white")

    # estado de la partida
    if board.is_checkmate():
        ganador = "Negras" if board.turn == chess.WHITE else "Blancas"
        status.config(text="Jaque mate - Ganan las " + ganador)
    elif board.is_game_over():
        status.config(text="Partida terminada: " + board.result())
    else:
        status.config(
            text="Tu turno de jugar - Blancas" if board.turn == chess.WHITE
            else "Turno de del pc"
        )


#para mostrar la evaluación
def formato_score(score):

    score = score.white()

    if score.is_mate():
        return "#" + str(score.mate())

    return f"{score.score() / 100:+.2f}"



#Como análisis (util más adelante para calcular el estilo de juego según amenazas)
def analizar_posicion():

    analysis_text.config(state="normal")
    analysis_text.delete("1.0", "end")

    if not board.is_game_over():

        infos = engine.analyse(
            board,
            chess.engine.Limit(time=TIEMPO_ANALISIS),
            multipv=LINEAS
        )

        for i, info in enumerate(infos, start=1):

            jugadas = board.variation_san(info["pv"][:8])

            analysis_text.insert(
                "end",
                f"{i}.  {formato_score(info['score'])}   profundidad {info['depth']}\n"
                f"{jugadas}\n\n"
            )

    analysis_text.config(state="disabled")



#metodo para que el pc juegue segun el lvl elegido por el usuario
def stockfish_move():

    if board.is_game_over():
        update_board()
        return

    analizar_posicion()
    root.update_idletasks()

    skill, tiempo = NIVELES[nivel_var.get()]

    engine.configure({"Skill Level": skill})
    result = engine.play(board, chess.engine.Limit(time=tiempo))
    engine.configure({"Skill Level": 20})   

    board.push(result.move)
    update_board()
    root.update_idletasks()
    analizar_posicion()


#para leer el movimiento del usuario
def on_square_click(event):

    global selected_square

    if board.turn != chess.WHITE or board.is_game_over():
        return

    lado, x0, y0 = medidas()

    col = int((event.x - x0) // lado)
    row = int((event.y - y0) // lado)

    if not (0 <= col < 8 and 0 <= row < 8):
        return

    square = chess.square(col, 7 - row)
    piece = board.piece_at(square)

    if selected_square is None:

        if piece and piece.color == chess.WHITE:
            selected_square = square
            update_board()

        return

    promotion = None
    moving_piece = board.piece_at(selected_square)

    if moving_piece and moving_piece.piece_type == chess.PAWN:
        if chess.square_rank(square) == 7:
            promotion = chess.QUEEN

    move = chess.Move(selected_square, square, promotion=promotion)

    if move in board.legal_moves:

        board.push(move)
        selected_square = None

        update_board()
        root.update_idletasks()

        stockfish_move()

    else:

        if piece and piece.color == chess.WHITE:
            selected_square = square
        else:
            selected_square = None

        update_board()


canvas.bind("<Button-1>", on_square_click)
canvas.bind("<Configure>", lambda event: update_board())





#metodo para nueva partida
def new_game():

    global board, selected_square

    board = chess.Board()
    selected_square = None

    update_board()
    root.update_idletasks()
    analizar_posicion()


tk.Label(controles, text="Nivel:", font=("Arial", 12),
         bg=FONDO, fg="white").pack(side="left", padx=(0, 6))

nivel_var = tk.StringVar(value="Intermedio")

menu_nivel = tk.OptionMenu(controles, nivel_var, *NIVELES.keys())
menu_nivel.config(font=("Arial", 12), width=12)
menu_nivel.pack(side="left", padx=(0, 20))

new_button = tk.Button(
    controles,
    text="Nueva partida",
    font=("Arial", 12),
    command=new_game
)
new_button.pack(side="left")



def close_app():

    engine.quit()
    root.destroy()


root.protocol("WM_DELETE_WINDOW", close_app)


update_board()
root.update_idletasks()
analizar_posicion()

root.mainloop()