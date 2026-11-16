import customtkinter as ctk

import usuarios
from campeon import mostrar_campeon

# COLORES (LOS MISMOS DEL TABLERO)
FONDO = "#282828"
TARJETA = "#2E1A33"
TARJETA_HOVER = "#45264D"
MORADO = "#8B5696"
MORADO_BOTON = "#7B3FD6"
CREMA = "#EEEED2"

usuario = None          # cuenta con la sesión iniciada
cerrar_tablero = None   # apaga Stockfish si cierras la ventana jugando


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
    global cerrar_tablero
    if usuario is None:
        abrir_login(jugar)          # primero inicia sesión y luego abre el tablero
        return
    from tablero import mostrar_tablero
    for elemento in pantalla_tablero.winfo_children():
        elemento.destroy()
    # el tablero se arma antes de ocultar el menú: si algo falla (p. ej. Stockfish), el menú sigue visible
    cerrar_tablero = mostrar_tablero(ventana, pantalla_tablero, usuario, volver_tablero)
    inicio.pack_forget()
    pantalla_tablero.pack(fill="both", expand=True)


def volver_tablero():
    global cerrar_tablero
    cerrar_tablero = None
    pantalla_tablero.pack_forget()
    inicio.pack(fill="both", expand=True)


def salir():
    if cerrar_tablero:
        cerrar_tablero()
    ventana.destroy()


def cerrar_sesion():
    global usuario
    usuario = None
    pintar_sesion()


# VENTANA DE INICIO DE SESION / REGISTRO
def abrir_login(despues=None):
    d = ctk.CTkToplevel(ventana)
    d.title("Kingship · Cuenta")
    d.geometry("360x420")
    d.configure(fg_color=FONDO)
    d.transient(ventana)
    d.after(100, d.grab_set)
    ctk.CTkLabel(d, text="Tu cuenta", font=("Georgia", 30, "bold"), text_color=CREMA).pack(pady=(26, 4))
    ctk.CTkLabel(d, text="Entra o crea una cuenta para guardar tus partidas",
                 font=("Segoe UI", 13), text_color="gray", wraplength=290).pack(pady=(0, 14))
    nombre = ctk.CTkEntry(d, placeholder_text="Usuario", width=260, height=40, fg_color=TARJETA, border_color=MORADO)
    nombre.pack(pady=6)
    clave = ctk.CTkEntry(d, placeholder_text="Clave", show="•", width=260, height=40, fg_color=TARJETA, border_color=MORADO)
    clave.pack(pady=6)
    error = ctk.CTkLabel(d, text="", font=("Segoe UI", 13), text_color="#E5534B", wraplength=290)
    error.pack(pady=(4, 6))

    def enviar(accion):
        global usuario
        ok, msg = accion(nombre.get(), clave.get())
        if not ok:
            error.configure(text=msg)
            return
        usuario = msg
        d.destroy()
        pintar_sesion()
        if despues:
            despues()

    ctk.CTkButton(d, text="Entrar", font=("Segoe UI", 17, "bold"), fg_color=MORADO_BOTON, hover_color=MORADO,
                  corner_radius=14, width=260, height=44, command=lambda: enviar(usuarios.entrar)).pack(pady=(4, 8))
    ctk.CTkButton(d, text="Crear cuenta", font=("Segoe UI", 17, "bold"), fg_color=FONDO, hover_color=TARJETA,
                  border_color=MORADO_BOTON, border_width=2, corner_radius=14, width=260, height=44,
                  command=lambda: enviar(usuarios.registrar)).pack()
    clave.bind("<Return>", lambda e: enviar(usuarios.entrar))


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
ventana.geometry("1100x740")
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

# BARRA DE SESION (arriba a la derecha)
barra_sesion = ctk.CTkFrame(inicio, fg_color=FONDO)
barra_sesion.pack(fill="x", padx=24, pady=(14, 0))


def pintar_sesion():
    for elemento in barra_sesion.winfo_children():
        elemento.destroy()
    if usuario:
        ctk.CTkButton(barra_sesion, text="Cerrar sesión", width=120, height=34, fg_color=FONDO, hover_color=TARJETA,
                      border_color=MORADO_BOTON, border_width=2, corner_radius=12, command=cerrar_sesion).pack(side="right", padx=(8, 0))
        ctk.CTkLabel(barra_sesion, text="👤 " + usuario, font=("Segoe UI", 15, "bold"), text_color=CREMA).pack(side="right", padx=8)
    else:
        ctk.CTkButton(barra_sesion, text="Entrar / Registrarse", width=180, height=34, fg_color=MORADO_BOTON,
                      hover_color=MORADO, corner_radius=12, command=abrir_login).pack(side="right")


pintar_sesion()

# TITULO
ctk.CTkLabel(inicio, text="♚", font=("Segoe UI Symbol", 48), text_color=CREMA).pack(pady=(0, 0))
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