import customtkinter as ctk

# COLORES
FONDO = "#282828"
TARJETA = "#2E1A33"
MORADO = "#8B5696"
MORADO_BOTON = "#7B3FD6"
CREMA = "#EEEED2"

# DATOS DE LOS CAMPEONES
datos = {
    "Tal": {
        "pieza": "♞",
        "nombre": "Mijaíl Tal",
        "titulo": "Campeón mundial 1960-1961 · Letonia",
        "estilo": "Ataque",
        "sabias": [
            "Le decían «el Mago de Riga» por sus ataques llenos de sacrificios.",
            "Fue campeón mundial con solo 23 años, el más joven de su época.",
            "Su idea era llevar al rival a posiciones tan complicadas que solo uno pudiera salir.",
        ],
    },
    "Petrosian": {
        "pieza": "♜",
        "nombre": "Tigran Petrosian",
        "titulo": "Campeón mundial 1963-1969 · Armenia",
        "estilo": "Defensa",
        "sabias": [
            "Le decían «Tigran de Hierro» porque era casi imposible ganarle.",
            "Pasó todo un año sin perder una sola partida antes de ser campeón.",
            "Le cortó a Bobby Fischer una racha de 20 victorias seguidas.",
        ],
    },
    "Karpov": {
        "pieza": "♛",
        "nombre": "Anatoli Kárpov",
        "titulo": "Campeón mundial 1975-1985 · Rusia",
        "estilo": "Posicional",
        "sabias": [
            "Asfixiaba a sus rivales acumulando pequeñas ventajas poco a poco.",
            "Jugó cinco mundiales contra Kaspárov: ¡144 partidas, 104 de ellas tablas!",
            "Fue campeón dos veces: de 1975 a 1985 y de nuevo de 1993 a 1999.",
        ],
    },
    "Capablanca": {
        "pieza": "♝",
        "nombre": "José Raúl Capablanca",
        "titulo": "Campeón mundial 1921-1927 · Cuba",
        "estilo": "Técnica",
        "sabias": [
            "Muchos lo consideran el jugador más talentoso de la historia.",
            "Estuvo ocho años seguidos sin perder una partida.",
            "Era famoso por su precisión en los finales: los hacía parecer fáciles.",
        ],
    },
    "Carlsen": {
        "pieza": "♚",
        "nombre": "Magnus Carlsen",
        "titulo": "Campeón mundial 2013-2023 · Noruega",
        "estilo": "Universal",
        "sabias": [
            "Tiene el rating más alto de la historia del ajedrez.",
            "Fue campeón del mundo en clásico, rápido y blitz al mismo tiempo.",
            "Jugó 125 partidas clásicas seguidas sin perder.",
        ],
    },
}


# PANTALLA DEL CAMPEON (SE DIBUJA DENTRO DE LA MISMA VENTANA)
def mostrar_campeon(contenedor, nombre, volver):
    c = datos[nombre]

    # encabezado
    ctk.CTkLabel(contenedor, text=c["pieza"], font=("Segoe UI Symbol", 80), text_color=CREMA).pack(pady=(25, 0))
    ctk.CTkLabel(contenedor, text=c["nombre"], font=("Georgia", 38, "bold"), text_color=CREMA).pack()
    ctk.CTkLabel(contenedor, text=c["titulo"], font=("Segoe UI", 15), text_color="gray").pack(pady=(2, 12))

    # etiqueta del estilo
    ctk.CTkLabel(contenedor, text="Estilo: " + c["estilo"], font=("Segoe UI", 15, "bold"),
                 fg_color=MORADO, text_color="white", corner_radius=16, width=190, height=34).pack(pady=(0, 22))

    # cuadro de datos curiosos
    cuadro = ctk.CTkFrame(contenedor, fg_color=TARJETA, border_color=MORADO, border_width=2, corner_radius=20)
    cuadro.pack(padx=120, fill="x")
    ctk.CTkLabel(cuadro, text="¿Sabías que...?", font=("Segoe UI", 20, "bold"), text_color=CREMA).pack(pady=(18, 6))
    for dato in c["sabias"]:
        ctk.CTkLabel(cuadro, text="♟   " + dato, font=("Segoe UI", 15), text_color=CREMA,
                     wraplength=650, justify="left").pack(anchor="w", padx=30, pady=5)
    ctk.CTkLabel(cuadro, text="", height=10).pack()

    # boton para volver al inicio
    ctk.CTkButton(contenedor, text="← Volver", font=("Segoe UI", 17, "bold"), fg_color=MORADO_BOTON,
                  hover_color=MORADO, corner_radius=14, width=180, height=46,
                  command=volver).pack(pady=25)