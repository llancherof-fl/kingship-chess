"""Tablero de Kingship: juega contra Stockfish, arrastra las piezas y guarda tus partidas.
Se dibuja dentro de la ventana de inicio.py (mostrar_tablero). También se puede abrir solo:  python tablero.py [usuario]"""
import datetime
import os
import sys
import threading
import tkinter as tk

import chess
import chess.engine
import chess.pgn
import customtkinter as ctk

import usuarios

try:
    from PIL import Image, ImageTk
    PILLOW_OK = True
except ImportError:
    PILLOW_OK = False

AQUI = os.path.dirname(os.path.abspath(__file__))
STOCKFISH_PATH = os.path.join(os.path.dirname(__file__), "stockfish", "stockfish-windows-x86-64-universal.exe")
CARPETA_PIEZAS = os.path.join(AQUI, "piezas")

# Niveles: (Skill Level de Stockfish, segundos que piensa)
NIVELES = {"Principiante": (0, 0.1), "Fácil": (4, 0.2), "Intermedio": (9, 0.4), "Avanzado": (15, 0.6), "GM": (20, 1.0)}

# Colores (los mismos del menú)
FONDO, TARJETA, MORADO, MORADO_BOTON, CREMA = "#282828", "#2E1A33", "#8B5696", "#7B3FD6", "#EEEED2"
CLARA, OSCURA, SELECCION, ULTIMA, JAQUE = "#EEEED2", "#8B5696", "#F6F669", "#BACA44", "#E5534B"
PIEZAS_CORONACION = [chess.QUEEN, chess.KNIGHT, chess.ROOK, chess.BISHOP]

# ---------- piezas (carpeta piezas/) ----------
originales, cache, cache_tam = {}, {}, 0
if PILLOW_OK:
    for c in "wb":
        for t in "KQRBNP":
            ruta = os.path.join(CARPETA_PIEZAS, c + t + ".png")
            if os.path.exists(ruta):
                originales[c + t] = Image.open(ruta).convert("RGBA")
USAR_IMAGENES = len(originales) == 12


def imagen(pieza, tam):
    global cache_tam
    if tam != cache_tam:
        cache.clear()
        cache_tam = tam
    clave = (pieza.color, pieza.piece_type, tam)
    if clave not in cache:
        nombre = ("w" if pieza.color else "b") + pieza.symbol().upper()
        cache[clave] = ImageTk.PhotoImage(originales[nombre].resize((tam, tam), Image.LANCZOS))
    return cache[clave]


def mostrar_tablero(raiz, contenedor, usuario, volver):
    """Dibuja el tablero dentro de `contenedor` (un frame de la ventana `raiz`).
    usuario: nombre de la cuenta (None = no se guardan partidas).  volver: función que muestra el menú.
    Devuelve cerrar(): apaga Stockfish (llámala si se cierra la ventana)."""
    board = chess.Board()

    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
    bloqueo_motor = threading.Lock()
    color_usuario = chess.WHITE
    sel = None            # casilla seleccionada
    arrastre = None       # pieza que se está arrastrando
    items = {}            # casilla -> elemento del canvas
    generacion = 0        # sube con cada partida nueva; descarta jugadas del motor viejas
    ocupado = False       # True mientras el motor piensa o una pieza se anima
    guardada = False
    promo = None          # (origen, destino) de un peón que espera que elijas la pieza
    cerrado = False       # True cuando sales del tablero

    # ---------- ventana ----------
    contenedor.grid_columnconfigure(0, weight=1)
    contenedor.grid_rowconfigure(0, weight=1)

    izq = ctk.CTkFrame(contenedor, fg_color=FONDO)
    izq.grid(row=0, column=0, sticky="nsew", padx=(16, 8), pady=16)
    izq.grid_columnconfigure(0, weight=1)
    izq.grid_rowconfigure(1, weight=1)
    estado = ctk.CTkLabel(izq, text="", font=("Segoe UI", 20, "bold"), text_color=CREMA)
    estado.grid(row=0, column=0, pady=(0, 6))
    canvas = tk.Canvas(izq, bg=FONDO, highlightthickness=0)
    canvas.grid(row=1, column=0, sticky="nsew")

    der = ctk.CTkFrame(contenedor, fg_color=TARJETA, border_color=MORADO, border_width=2, corner_radius=20, width=330)
    der.grid(row=0, column=1, sticky="ns", padx=(8, 16), pady=16)
    der.pack_propagate(False)
    etiqueta = lambda t: ctk.CTkLabel(der, text=t, font=("Segoe UI", 13, "bold"), text_color="#B98CC4").pack(anchor="w", padx=24, pady=(10, 2))

    ctk.CTkLabel(der, text="♚ KINGSHIP", font=("Georgia", 28, "bold"), text_color=CREMA).pack(pady=(18, 0))
    ctk.CTkLabel(der, text=("👤 " + usuario) if usuario else "Sin sesión: no se guardarán partidas",
                 font=("Segoe UI", 13), text_color="gray").pack(pady=(0, 6))
    etiqueta("JUEGAS CON")
    color_var = ctk.CTkSegmentedButton(der, values=["Blancas", "Negras"], fg_color=FONDO, unselected_color=FONDO,
                                       selected_color=MORADO_BOTON, selected_hover_color=MORADO,
                                       command=lambda v: cambiar_color())
    color_var.set("Blancas")
    color_var.pack(padx=24, fill="x")
    etiqueta("NIVEL DE STOCKFISH")
    nivel_var = ctk.CTkOptionMenu(der, values=list(NIVELES), fg_color=MORADO_BOTON, button_color=MORADO,
                                  button_hover_color=MORADO_BOTON, dropdown_fg_color=TARJETA, height=34)
    nivel_var.set("Intermedio")
    nivel_var.pack(padx=24, fill="x")
    boton = lambda t, cmd, relleno=True: ctk.CTkButton(
        der, text=t, command=cmd, font=("Segoe UI", 16, "bold"), height=42, corner_radius=14,
        fg_color=MORADO_BOTON if relleno else TARJETA, hover_color=MORADO if relleno else FONDO,
        border_color=MORADO_BOTON, border_width=0 if relleno else 2).pack(padx=24, pady=(10, 0), fill="x")
    boton("Nueva partida", lambda: nueva())
    boton("Guardar partida", lambda: guardar(), relleno=False)
    boton("← Menú", lambda: salir(), relleno=False)
    mensaje = ctk.CTkLabel(der, text="", font=("Segoe UI", 13), text_color="#B98CC4", wraplength=280)
    mensaje.pack(pady=(8, 0))
    etiqueta("JUGADAS")
    lista_txt = ctk.CTkTextbox(der, fg_color=FONDO, text_color=CREMA, font=("Consolas", 13), wrap="word", state="disabled")
    lista_txt.pack(padx=20, pady=(0, 18), fill="both", expand=True)


    # ---------- geometría ----------
    def medidas():
        ancho, alto = canvas.winfo_width(), canvas.winfo_height()
        lado = (min(ancho, alto) - 56) / 8
        return lado, (ancho - 8 * lado) / 2, (alto - 8 * lado) / 2


    def esquina(sq, lado, x0, y0):
        col, fila = chess.square_file(sq), 7 - chess.square_rank(sq)
        if color_usuario == chess.BLACK:                  # tablero volteado si juegas con negras
            col, fila = 7 - col, 7 - fila
        return x0 + col * lado, y0 + fila * lado


    def casilla_en(x, y):
        lado, x0, y0 = medidas()
        col, fila = int((x - x0) // lado), int((y - y0) // lado)
        if not (0 <= col < 8 and 0 <= fila < 8):
            return None
        if color_usuario == chess.BLACK:
            col, fila = 7 - col, 7 - fila
        return chess.square(col, 7 - fila)


    # ---------- dibujo ----------
    def dibujar():
        nonlocal items
        canvas.delete("all")
        items = {}
        lado, x0, y0 = medidas()
        if lado <= 0:
            return
        m, N = 10, 8 * lado
        canvas.create_rectangle(x0 - m + 6, y0 - m + 8, x0 + N + m + 6, y0 + N + m + 8, fill="#141414", outline="")   # sombra
        canvas.create_rectangle(x0 - m, y0 - m, x0 + N + m, y0 + N + m, fill=TARJETA, outline=MORADO, width=2)       # marco
        ultimo = board.peek() if board.move_stack else None
        rey = board.king(board.turn) if board.is_check() else None
        for sq in chess.SQUARES:
            x, y = esquina(sq, lado, x0, y0)
            c = CLARA if (chess.square_file(sq) + chess.square_rank(sq)) % 2 else OSCURA
            if ultimo and sq in (ultimo.from_square, ultimo.to_square):
                c = ULTIMA
            if sq == sel:
                c = SELECCION
            if sq == rey:
                c = JAQUE
            canvas.create_rectangle(x, y, x + lado, y + lado, fill=c, outline="")
        for i in range(8):                                # coordenadas
            letra = "abcdefgh"[i if color_usuario else 7 - i]
            numero = str(8 - i if color_usuario else i + 1)
            canvas.create_text(x0 + i * lado + lado / 2, y0 + N + m + 12, text=letra, fill="#B98CC4", font=("Segoe UI", 11, "bold"))
            canvas.create_text(x0 - m - 12, y0 + i * lado + lado / 2, text=numero, fill="#B98CC4", font=("Segoe UI", 11, "bold"))
        if sel is not None:                               # casillas a las que puede ir la pieza
            for mv in board.legal_moves:
                if mv.from_square == sel:
                    x, y = esquina(mv.to_square, lado, x0, y0)
                    cx, cy = x + lado / 2, y + lado / 2
                    if board.piece_at(mv.to_square) or board.is_en_passant(mv):
                        r = lado * 0.44
                        canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline="#5a7d3a", width=max(3, lado * 0.07))
                    else:
                        r = lado * 0.16
                        canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill="#5a7d3a", outline="")
        for sq in chess.SQUARES:
            p = board.piece_at(sq)
            if p:
                x, y = esquina(sq, lado, x0, y0)
                cx, cy = x + lado / 2, y + lado / 2
                if USAR_IMAGENES:
                    items[sq] = canvas.create_image(cx, cy, image=imagen(p, int(lado * 0.95)))
                else:
                    items[sq] = canvas.create_text(cx, cy, text=p.unicode_symbol(), font=("Segoe UI Symbol", int(lado * 0.7)), fill="black")
        if promo:                                         # selector: ¿en qué pieza corona el peón?
            o, d = promo
            x, ys = columna_promo(lado, x0, y0)
            canvas.coords(items[o], x + lado / 2, ys[0] + lado / 2)
            canvas.create_rectangle(x - 4, min(ys) - 4, x + lado + 4, max(ys) + lado + 4, fill=TARJETA, outline=SELECCION, width=3)
            for yy, t in zip(ys, PIEZAS_CORONACION):
                canvas.create_rectangle(x, yy, x + lado, yy + lado, fill=CREMA, outline=MORADO, width=2)
                p = chess.Piece(t, color_usuario)
                if USAR_IMAGENES:
                    canvas.create_image(x + lado / 2, yy + lado / 2, image=imagen(p, int(lado * 0.95)))
                else:
                    canvas.create_text(x + lado / 2, yy + lado / 2, text=p.unicode_symbol(), font=("Segoe UI Symbol", int(lado * 0.7)), fill="black")


    def columna_promo(lado, x0, y0):
        """Columna de 4 casillas desde el destino hacia el interior del tablero."""
        x, y = esquina(promo[1], lado, x0, y0)
        baja = y < y0 + 4 * lado
        return x, [y + i * lado if baja else y - i * lado for i in range(4)]


    def animar(mv, fin):
        """Desliza la pieza de su casilla a la de destino y luego llama a fin()."""
        lado, x0, y0 = medidas()
        item = items.get(mv.from_square)
        if item is None:
            fin()
            return
        xa, ya = esquina(mv.from_square, lado, x0, y0)
        xb, yb = esquina(mv.to_square, lado, x0, y0)
        canvas.tag_raise(item)

        def paso(i):
            if cerrado:
                return
            e = 1 - (1 - i / 14) ** 3                     # suaviza el final
            canvas.coords(item, xa + (xb - xa) * e + lado / 2, ya + (yb - ya) * e + lado / 2)
            raiz.after(15, paso, i + 1) if i < 14 else fin()
        paso(1)


    def lista():
        b, partes = chess.Board(), []
        for i, mv in enumerate(board.move_stack):
            if i % 2 == 0:
                partes.append(f"{i // 2 + 1}.")
            partes.append(b.san(mv))
            b.push(mv)
        lista_txt.configure(state="normal")
        lista_txt.delete("1.0", "end")
        lista_txt.insert("end", " ".join(partes))
        lista_txt.configure(state="disabled")
        lista_txt.see("end")


    def texto_estado():
        if board.is_checkmate():
            return "Jaque mate · ganan las " + ("negras" if board.turn else "blancas")
        if board.is_game_over():
            return "Partida terminada · " + board.result()
        if board.turn == color_usuario:
            return "Tu turno" + (" · ¡jaque!" if board.is_check() else "")
        return "Stockfish está pensando…"


    def refrescar():
        dibujar()
        lista()
        estado.configure(text=texto_estado())


    def avisar(texto):
        mensaje.configure(text=texto)
        def borrar():
            try:
                if mensaje.cget("text") == texto:
                    mensaje.configure(text="")
            except tk.TclError:                           # ya saliste del tablero
                pass
        raiz.after(4000, borrar)


    # ---------- jugadas ----------
    def hacer(mv, animado):
        nonlocal sel, ocupado
        sel, ocupado = None, True

        def listo():
            nonlocal ocupado
            board.push(mv)
            ocupado = False
            refrescar()
            if board.is_game_over():
                if usuario:
                    guardar(auto=True)
            elif board.turn != color_usuario:
                turno_motor()
        animar(mv, listo) if animado else listo()


    def turno_motor():
        nonlocal ocupado
        ocupado = True
        estado.configure(text=texto_estado())
        gen, (skill, tiempo), tab, res = generacion, NIVELES[nivel_var.get()], board.copy(), {}

        def trabajo():                                    # el motor piensa sin congelar la ventana
            with bloqueo_motor:
                try:
                    engine.configure({"Skill Level": skill})
                    res["mv"] = engine.play(tab, chess.engine.Limit(time=tiempo)).move
                except Exception:                         # el motor se cerró al salir del tablero
                    pass
        hilo = threading.Thread(target=trabajo, daemon=True)
        hilo.start()

        def esperar():
            if gen != generacion:                         # empezaste otra partida: se descarta
                return
            if hilo.is_alive():
                raiz.after(30, esperar)
            elif "mv" in res:
                hacer(res["mv"], True)
            else:
                avisar("El motor no respondió. Revisa la ruta de Stockfish.")
        esperar()


    def intentar(o, d, animado):
        nonlocal promo, sel
        p = board.piece_at(o)
        if p and p.piece_type == chess.PAWN and chess.square_rank(d) in (0, 7):
            if chess.Move(o, d, promotion=chess.QUEEN) in board.legal_moves:
                promo, sel = (o, d), None
                dibujar()                                 # muestra el selector
                return True
            return False
        mv = chess.Move(o, d)
        if mv in board.legal_moves:
            hacer(mv, animado)
            return True
        return False


    def bloqueado():
        return ocupado or board.is_game_over() or board.turn != color_usuario


    def elegir_coronacion(e):
        nonlocal promo
        o, d = promo
        lado, x0, y0 = medidas()
        x, ys = columna_promo(lado, x0, y0)
        for yy, t in zip(ys, PIEZAS_CORONACION):
            if x <= e.x < x + lado and yy <= e.y < yy + lado:
                promo = None
                hacer(chess.Move(o, d, promotion=t), False)
                return
        promo = None                                      # clic fuera: se cancela y el peón vuelve
        dibujar()


    def presionar(e):
        nonlocal sel, arrastre
        if bloqueado():
            return
        if promo:
            elegir_coronacion(e)
            return
        sq = casilla_en(e.x, e.y)
        if sq is None:
            return
        if sel is not None and sq != sel and intentar(sel, sq, True):      # clic en la casilla de destino
            return
        p = board.piece_at(sq)
        if p and p.color == color_usuario:
            sel = sq
            dibujar()
            arrastre = items[sq]
            canvas.tag_raise(arrastre)
            canvas.coords(arrastre, e.x, e.y)
        else:
            sel = None
            dibujar()


    def mover(e):
        if arrastre is not None:
            canvas.coords(arrastre, e.x, e.y)


    def soltar(e):
        nonlocal sel, arrastre
        if arrastre is None:
            return
        arrastre = None
        sq = casilla_en(e.x, e.y)
        if sq is not None and sq != sel and intentar(sel, sq, False):
            return
        if sq != sel:
            sel = None
        dibujar()


    canvas.bind("<ButtonPress-1>", presionar)
    canvas.bind("<B1-Motion>", mover)
    canvas.bind("<ButtonRelease-1>", soltar)
    canvas.bind("<Configure>", lambda e: dibujar())


    # ---------- partida y guardado ----------
    def guardar(auto=False):
        nonlocal guardada
        if not usuario:
            avisar("Entra con tu cuenta desde el menú para guardar partidas.")
            return
        if not board.move_stack:
            avisar("Todavía no hay jugadas.")
            return
        if guardada:
            avisar("Esta partida ya está guardada.")
            return
        g = chess.pgn.Game.from_board(board)
        yo, sf = usuario, "Stockfish"
        g.headers["Event"] = f"Partida vs Stockfish ({nivel_var.get()})"
        g.headers["Site"] = "Kingship"
        g.headers["Date"] = datetime.date.today().strftime("%Y.%m.%d")
        g.headers["White"], g.headers["Black"] = (yo, sf) if color_usuario == chess.WHITE else (sf, yo)
        g.headers["Result"] = board.result() if board.is_game_over() else "*"
        usuarios.guardar_pgn(usuario, str(g))
        guardada = True
        avisar("Partida terminada y guardada ✓" if auto else "Partida guardada ✓")


    def nueva():
        nonlocal board, sel, generacion, guardada, ocupado, color_usuario, promo
        promo = None
        generacion += 1
        board, sel, guardada, ocupado = chess.Board(), None, False, False
        color_usuario = chess.WHITE if color_var.get() == "Blancas" else chess.BLACK
        refrescar()
        if color_usuario == chess.BLACK:
            turno_motor()


    def cambiar_color():
        if board.move_stack and not board.is_game_over():
            avisar("El cambio de color vale desde la próxima partida.")
        else:
            nueva()


    def cerrar():
        """Apaga Stockfish y descarta jugadas pendientes (al volver al menú o al cerrar la ventana)."""
        nonlocal generacion, cerrado
        if cerrado:
            return
        cerrado = True
        generacion += 1
        engine.quit()


    def salir():
        cerrar()
        volver()


    if not USAR_IMAGENES:
        avisar("Instala Pillow (pip install pillow) para ver las piezas de la carpeta piezas.")
    refrescar()
    return cerrar



if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ventana = ctk.CTk()
    ventana.title("Kingship")
    ventana.geometry("1100x720")
    ventana.minsize(900, 600)
    ventana.configure(fg_color=FONDO)
    marco = ctk.CTkFrame(ventana, fg_color=FONDO)
    marco.pack(fill="both", expand=True)
    cerrar_todo = mostrar_tablero(ventana, marco, sys.argv[1] if len(sys.argv) > 1 else None, ventana.destroy)
    ventana.protocol("WM_DELETE_WINDOW", lambda: (cerrar_todo(), ventana.destroy()))
    ventana.mainloop()
