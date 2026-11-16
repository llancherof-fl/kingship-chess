import os
import subprocess
import sys
import tkinter as tk

import customtkinter as ctk
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageOps, ImageTk

import analizar_jugador
from analizar_partida import analizar_partida, modelo, columnas
from campeon import datos

# Evita que Windows escale los widgets pero no las imágenes del canvas
ctk.set_widget_scaling(1.0)
ctk.set_window_scaling(1.0)

# COLORES
BLANCO = "#FCFCFD"
MORADO = "#550469"
MORADO_CLARO = "#8B5696"
NEGRO = "#101010"
BORDE = "#B04FD0"
TARJETA = "#EABDF2"
NARANJA = "#F5A800"
TEXTO = "#4E4E4E"
GRIS = "#666666"

#FONTS
BODY = ("League Spartan", 16)
BODYBOLD = ("League Spartan", 16, "bold")
SMALLBODY = ("League Spartan", 12)
TITLE = ("League Spartan", 58, "bold")
SUBTITLE = ("League Spartan", 21, "bold")

# MEDIDAS
ANCHO = 1170
BANNER = (1170, 345)
FOOTER = (1170, 355)
FOTO = (272, 324)
PIEZAS = (115, 115)
CARD = (244, 220)
MINI = (90, 90)
CORONA = (33, 33)

CARPETA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imagenes")

def abrir(nombre, tam, relleno="#D9A8EE"):
    """Abre un PNG redimensionado; si no existe, devuelve un relleno para poder probar."""
    ruta = os.path.join(CARPETA, nombre)
    if os.path.exists(ruta):
        return Image.open(ruta).convert("RGBA").resize(tam, Image.LANCZOS)
    return Image.new("RGBA", tam, relleno)


def tarjeta_img():
    return ImageTk.PhotoImage(abrir("tarjeta.png", CARD))

def tablero_img():
    return ImageTk.PhotoImage(abrir("tablero.png", MINI))

def foto_hero(campeon, tam=FOTO):
    propia = os.path.join(CARPETA, f"{campeon.lower()}.png")

    if os.path.exists(propia):
        im = ImageOps.fit(
            Image.open(propia).convert("RGBA"),
            tam,
            Image.LANCZOS
        )

        mascara = Image.new("L", tam, 0)
        ImageDraw.Draw(mascara).rounded_rectangle(
            (0, 0, tam[0], tam[1]),
            30,
            fill=255
        )
        im.putalpha(mascara)

    else:
        im = abrir("foto.png", tam, (0, 0, 0, 0))

    return ImageTk.PhotoImage(im)


def para_ctk(nombre, tam, relleno="#D9A8EE"):
    im = abrir(nombre, (tam[0] * 2, tam[1] * 2), relleno)
    return ctk.CTkImage(light_image=im, dark_image=im, size=tam)

def partidas_similares(campeon, x, n=3):
    d = pd.read_csv("base_entrenamiento.csv").drop_duplicates()
    d = d[d["campeon"] == campeon].copy()
    X = (d[columnas].values - np.array(modelo["media"])) / np.array(modelo["escala"])
    d["dist"] = np.linalg.norm(X - x, axis=1)
    return d.sort_values("dist").drop_duplicates("partida").head(n)["partida"].tolist()


def texto_explicacion(campeon, estilo):
    top = sorted(estilo, key=estilo.get, reverse=True)[:3]
    n = [t.replace("_", " ") for t in top]
    return (f"Tus dimensiones más marcadas fueron {n[0]}, {n[1]} y {n[2]}. "
            f"Esa combinación se parece al juego de {datos[campeon]['nombre']}, "
            f"cuyo estilo se describe como {datos[campeon]['estilo'].lower()}.")


def reintentar():
    subprocess.Popen([sys.executable, "tablero.py"])
    ventana.destroy()


def barra(padre, texto, valor, color=MORADO):
    fila = ctk.CTkFrame(padre, fg_color="transparent")
    fila.pack(fill="x", padx=30, pady=3)
    ctk.CTkLabel(fila, text=texto, width=150, anchor="w", text_color=TEXTO,
                 font=("League Spartan", 14)).pack(side="left")
    b = ctk.CTkProgressBar(fila, progress_color=color, fg_color="#E9CFF5", height=12)
    b.set(valor / 100)
    b.pack(side="left", fill="x", expand=True, padx=10)
    ctk.CTkLabel(fila, text=f"{valor:.0f}%", width=50, text_color=TEXTO).pack(side="left")


def mostrar_fiabilidad(padre, etiqueta, acierto, partidas):
    # Colores según el nivel de fiabilidad
    if etiqueta == "FIABLE":
        color = "#269B63"
    elif etiqueta == "FIABILIDAD MEDIA":
        color = "#D99A00"
    elif etiqueta == "POCO FIABLE":
        color = "#C94B55"
    else:
        color = "#777777"

    # Contenedor
    panel = ctk.CTkFrame(
        padre,
        fg_color="transparent",
        corner_radius=0
    )
    panel.pack(fill="x", padx=203, pady=15)

    # Título
    ctk.CTkLabel(
        panel,
        text="Fiabilidad del análisis",
        font=BODYBOLD,
        text_color=NEGRO
    ).pack(anchor="w", padx=25, pady=(20, 5))

    # Porcentaje y estado
    fila = ctk.CTkFrame(panel, fg_color="transparent")
    fila.pack(fill="x", padx=25)

    if acierto is not None:
        porcentaje = acierto * 100
        texto = f"{porcentaje:.1f}%"
    else:
        porcentaje = 0
        texto = "--"

    ctk.CTkLabel(
        fila,
        text=texto,
        font=("League Spartan", 38, "bold"),
        text_color=color
    ).pack(side="left")

    ctk.CTkLabel(
        fila,
        text=etiqueta,
        font=BODYBOLD,
        text_color=color
    ).pack(side="left", padx=15)

    # Barra de fiabilidad
    progreso = ctk.CTkProgressBar(
        panel,
        height=13,
        progress_color=color,
        fg_color="#E9CFF5",
        corner_radius=10
    )
    progreso.set(porcentaje / 100)
    progreso.pack(fill="x", padx=25, pady=(10, 8))

    # Información adicional
    ctk.CTkLabel(
        panel,
        text=f"Evaluación basada en {partidas} partidas.",
        font=SMALLBODY,
        text_color=GRIS
    ).pack(anchor="w", padx=25, pady=(0, 20))

    return panel



def tarjeta_partida(padre, numero, texto):
    cv = tk.Canvas(padre, width=CARD[0], height=CARD[1], bg=BLANCO, highlightthickness=0)

    cv.pack(side="left", fill="both", expand=True, padx=10)

    def redibujar(e):
        w, h = e.width, e.height

        if w < 50 or h < 50:
            return

        cv.delete("all")

        fondo = ImageTk.PhotoImage(abrir("tarjeta.png", (w, h)))

        mini = tablero_img()

        cv.imagenes = [fondo, mini]

        cv.create_image(0, 0, anchor="nw", image=fondo)

        cv.create_text(w / 2, 26,text=f"Partida {numero}",fill=NEGRO,font=BODYBOLD)

        cv.create_image( w / 2, 108,image=mini)

        cv.create_text(w / 2, 184,text=texto,fill=TEXTO,width=w - 35, font=SMALLBODY,justify="center")

    cv.bind("<Configure>", redibujar)

    
def lienzo_imagen(padre, nombre, base, relleno, extra=None):
    """Canvas que se estira al ancho disponible manteniendo la proporción de la imagen."""
    cv = tk.Canvas(padre, height=base[1], bg=BLANCO, highlightthickness=0)
    cv.pack(fill="x")
    cv.ultimo = 0

    def redibujar(e):
        w = e.width
        if w < 50 or w == cv.ultimo:
            return
        cv.ultimo = w
        esc = w / base[0]
        h = int(base[1] * esc)
        cv.config(height=h)
        cv.delete("all")
        fondo = ImageTk.PhotoImage(abrir(nombre, (w, h), relleno))
        cv.imagenes = [fondo]            # evita que Python borre las imágenes
        cv.create_image(0, 0, anchor="nw", image=fondo)
        if extra:
            extra(cv, esc, w)

    cv.bind("<Configure>", redibujar)
    return cv

# pantalla
ctk.set_appearance_mode("light")
ventana = ctk.CTk()
ventana.title("Kingship - Resultados")
ventana.geometry("1210x760")
ventana.resizable(False, False)
ventana.configure(fg_color=BLANCO)

# barra superior
barra_sup = ctk.CTkFrame(ventana, fg_color=BLANCO, height=48, corner_radius=0)
barra_sup.pack(fill="x")
ctk.CTkLabel(barra_sup, image=para_ctk("logo.png", CORONA, (0, 0, 0, 0)), text="").pack(
    side="left", padx=(40, 8), pady=8)
ctk.CTkLabel(barra_sup, text="Kingship Resultados", font=("League Spartan", 18, "bold"),
             text_color=MORADO).pack(side="left")

pagina = ctk.CTkScrollableFrame(ventana, fg_color=BLANCO, corner_radius=0)
pagina.pack(fill="both", expand=True)

salida = analizar_partida("prueba.pgn", color=0)

if salida is None:
    ctk.CTkLabel(pagina, text="La partida fue muy corta para analizarla (mínimo 10 jugadas).",
                 text_color=TEXTO, font=("League Spartan", 16)).pack(pady=60)
    ctk.CTkButton(pagina, text="Volver a intentar →", fg_color=NARANJA, text_color="black",
                  hover_color="#D99700", command=reintentar).pack()
else:
    resultado, estilo, x = salida
    campeon = max(resultado, key=resultado.get)
    c = datos[campeon]

    fiabilidad = analizar_jugador.analizar_archivo("partidas_jugador.csv")
    if fiabilidad is not None:
        etiqueta = fiabilidad["etiqueta"]
        acierto = fiabilidad["acierto"]
        n_partidas = fiabilidad["partidas"]
        k = fiabilidad["ventana"]

    #Banner
    def dibujar_banner(cv, esc, w):
        foto = foto_hero(campeon, (int(FOTO[0] * esc), int(FOTO[1] * esc)))
        cv.imagenes.append(foto)
        cv.create_image(w - int(120 * esc), int(10 * esc), anchor="ne", image=foto)
        cv.create_text(int(70 * esc), int(120 * esc), anchor="w", text=c["nombre"], fill=MORADO,
                       font=TITLE, width=int(700 * esc))
        cv.create_text(int(70 * esc), int(185 * esc), anchor="w",
                       text=f"{c['titulo']}\nEstilo: {c['estilo']}", fill=NEGRO,
                       font=SUBTITLE, width=int(560 * esc))

    lienzo_imagen(pagina, "banner.png", BANNER, "#EBD0F5", dibujar_banner)

    #descripcion
    ctk.CTkLabel(pagina, text=f"Tu estilo de juego es similar a: {c['nombre']} ({resultado[campeon]}%)",
                 font=SUBTITLE, text_color=MORADO).pack(pady=(85,21))
    ctk.CTkFrame(pagina, fg_color="#D9A8EE", height=1, width=763.75).pack(padx = 203, anchor = "w")
    ctk.CTkLabel(pagina, text=texto_explicacion(campeon, estilo), wraplength=763.75, justify="left",
                 text_color=TEXTO, font=BODY).pack(pady=(21), padx=203, anchor = "w")
    # FIABILIDAD DEL ANALISIS
    if fiabilidad is not None:
        mostrar_fiabilidad(pagina, etiqueta, acierto, n_partidas)

    # TOP 3 PARTIDAS
    ctk.CTkLabel(pagina, text="Top 3 partidas recomendadas", font=BODYBOLD, text_color=NEGRO).pack(anchor="w", padx=203, pady=(21,10))
    ctk.CTkLabel(pagina, text="Utiliza estas partidas como referencia para estudiar nuevas jugadas, "
                 "descubrir estrategias y mejorar tu toma de decisiones en el tablero.",
                 wraplength=763.75, justify="left", font =BODY, text_color=TEXTO).pack(anchor="w", padx=203, pady=(0, 21))

    fila = ctk.CTkFrame(pagina, fg_color=BLANCO)
    fila.pack(fill="x", padx=(203))
    for i, p in enumerate(partidas_similares(campeon, x), 1):
        tarjeta_partida(fila, i, p)

    #Volver a jugar
    bloque = ctk.CTkFrame(pagina, fg_color=BLANCO)
    bloque.pack(pady=(51, 10), padx=203)
    ctk.CTkLabel(bloque, image=para_ctk("twoPieces.png", PIEZAS, (0, 0, 0, 0)), text="").pack(
        side="left", padx=0)
    txt = ctk.CTkFrame(bloque, fg_color=BLANCO)
    txt.pack(side="left")
    ctk.CTkLabel(txt, text="¿Quieres intentar otra partida?", font=BODYBOLD,
                 text_color=NEGRO).pack(anchor="w", padx = 21)
    ctk.CTkLabel(txt, text="Descubre nuevamente tu estilo de juego y pon a prueba tus habilidades.", font = BODY,
                 text_color=GRIS, wraplength=620, justify="left").pack(anchor="w", pady=6, padx = 21);
    ctk.CTkButton(txt, text="Volver a intentar →", font=BODY, fg_color=NARANJA,
                  text_color=NEGRO, hover_color="#D99700", corner_radius=20,
                  width=170, height=36, command=reintentar).pack(anchor="w", padx = 21)

    #cosos red neuronal
    ctk.CTkLabel(pagina, text="Procesos y cálculo de red neuronal", font=BODYBOLD,
                 text_color=NEGRO).pack(anchor="w", padx=203, pady=(20, 8))
    caja = ctk.CTkFrame(pagina,fg_color="transparent",corner_radius=0,border_width=0)
    caja.pack(fill="x", padx=203, pady=(0, 30))
    ctk.CTkLabel(caja, text="Parecido con cada campeón", font=BODYBOLD,
                 text_color=MORADO).pack(pady=(14, 4), padx=203, anchor="w")
    for nombre, v in sorted(resultado.items(), key=lambda kv: -kv[1]):
        barra(caja, nombre, v)
    ctk.CTkLabel(caja, text="Tus 10 nodos de estilo", font=BODYBOLD,
                 text_color=MORADO).pack(pady=(14, 4), padx=203, anchor="w")
    for nombre, v in estilo.items():
        barra(caja, nombre.replace("_", " "), v, "#8B5696")
    ctk.CTkLabel(caja, text="", height=8).pack()

    
    lienzo_imagen(pagina, "footer.png", FOOTER, "#55076B")

ventana.mainloop()