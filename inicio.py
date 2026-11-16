import customtkinter as ctk

from campeon import mostrar_campeon
from tablero import cerrar_motor, mostrar_tablero

# COLORES (LOS MISMOS DEL TABLERO)
FONDO = "#282828"
TARJETA = "#2E1A33"
TARJETA_HOVER = "#45264D"
MORADO = "#8B5696"
MORADO_BOTON = "#7B3FD6"
CREMA = "#EEEED2"


# CAMBIAR DE PANTALLA
def ver_campeon(nombre):
    inicio.pack_forget()
    for elemento in pantalla_campeon.winfo_children():
        elemento.destroy()
    mostrar_campeon(pantalla_campeon, nombre, volver)
    pantalla_campeon.pack(fill="both", expand=True)


def volver():
    pantalla_campeon.pack_forget()
    inicio.pack(fill="both", expand=True)


def jugar():
    inicio.pack_forget()
    if not pantalla_tablero.winfo_children():
        mostrar_tablero(pantalla_tablero, volver_del_tablero)
    pantalla_tablero.pack(fill="both", expand=True)


def volver_del_tablero():
    pantalla_tablero.pack_forget()
    inicio.pack(fill="both", expand=True)


def salir():
    cerrar_motor()
    ventana.destroy()


# TARJETA DE UN CAMPEON
def crear_tarjeta(padre, pieza, nombre, estilo):
    tarjeta = ctk.CTkFrame(padre, fg_color=TARJETA, border_color=MORADO, border_width=2,
                           corner_radius=20, width=180, height=200, cursor="hand2")
    tarjeta.pack(side="left", padx=10)
    tarjeta.pack_propagate(False)

    icono = ctk.CTkLabel(tarjeta, text=pieza, font=("Segoe UI Symbol", 58), text_color=CREMA)
    icono.pack(pady=(22, 4))
    titulo = ctk.CTkLabel(tarjeta, text=nombre, font=("Segoe UI", 18, "bold"), text_color=CREMA)
    titulo.pack()
    subtitulo = ctk.CTkLabel(tarjeta, text=estilo, font=("Segoe UI", 14), text_color="#B98CC4")
    subtitulo.pack()

    # clic y efecto al pasar el mouse en toda la tarjeta
    for parte in (tarjeta, icono, titulo, subtitulo):
        parte.bind("<Button-1>", lambda e: ver_campeon(nombre))
        parte.bind("<Enter>", lambda e: tarjeta.configure(fg_color=TARJETA_HOVER))
        parte.bind("<Leave>", lambda e: tarjeta.configure(fg_color=TARJETA))


# VENTANA
ctk.set_appearance_mode("dark")
ventana = ctk.CTk()
ventana.title("Kingship")
ventana.geometry("1100x700")
ventana.configure(fg_color=FONDO)
ventana.protocol("WM_DELETE_WINDOW", salir)

# PIE DE PAGINA Y FRANJA (SIEMPRE VISIBLES)
ctk.CTkLabel(ventana, text="Proyecto final · Matemáticas Discretas · Universidad del Norte · 2026",
             font=("Segoe UI", 12), text_color="gray").pack(side="bottom", pady=(4, 10))

franja = ctk.CTkFrame(ventana, fg_color=FONDO, height=28)
franja.pack(side="bottom", fill="x")
for i in range(40):
    if i % 2 == 0:
        color = MORADO
    else:
        color = CREMA
    ctk.CTkFrame(franja, fg_color=color, corner_radius=0, width=28, height=28).pack(side="left")

# PANTALLAS
inicio = ctk.CTkFrame(ventana, fg_color=FONDO)
pantalla_campeon = ctk.CTkFrame(ventana, fg_color=FONDO)
pantalla_tablero = ctk.CTkFrame(ventana, fg_color=FONDO)
inicio.pack(fill="both", expand=True)

# TITULO
ctk.CTkLabel(inicio, text="♚", font=("Segoe UI Symbol", 64), text_color=CREMA).pack(pady=(30, 0))
ctk.CTkLabel(inicio, text="KINGSHIP", font=("Georgia", 56, "bold"), text_color=CREMA).pack()
ctk.CTkLabel(inicio, text="¿A qué campeón de ajedrez te pareces?", font=("Segoe UI", 24, "bold"),
             text_color=CREMA).pack(pady=(4, 0))
ctk.CTkLabel(inicio, text="Juega contra Stockfish y descubre si tu estilo se parece al de los grandes campeones.",
             font=("Segoe UI", 15), text_color="gray").pack(pady=(6, 28))

# TARJETAS
fila = ctk.CTkFrame(inicio, fg_color=FONDO)
fila.pack()
crear_tarjeta(fila, "♞", "Tal", "Ataque")
crear_tarjeta(fila, "♜", "Petrosian", "Defensa")
crear_tarjeta(fila, "♛", "Karpov", "Posicional")
crear_tarjeta(fila, "♝", "Capablanca", "Técnica")
crear_tarjeta(fila, "♚", "Carlsen", "Universal")

ctk.CTkLabel(inicio, text="Haz clic en un campeón para conocerlo", font=("Segoe UI", 13),
             text_color="gray").pack(pady=(16, 22))

# BOTONES
botones = ctk.CTkFrame(inicio, fg_color=FONDO)
botones.pack()
ctk.CTkButton(botones, text="Jugar", font=("Segoe UI", 21, "bold"), fg_color=MORADO_BOTON,
              hover_color=MORADO, corner_radius=14, width=230, height=58,
              command=jugar).pack(side="left", padx=12)
ctk.CTkButton(botones, text="Salir", font=("Segoe UI", 21, "bold"), fg_color=FONDO,
              hover_color=TARJETA, border_color=MORADO_BOTON, border_width=2,
              corner_radius=14, width=230, height=58,
              command=salir).pack(side="left", padx=12)

ventana.mainloop()