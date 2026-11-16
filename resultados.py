import os
import tkinter as tk

import customtkinter as ctk
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageOps, ImageTk

import analizar_jugador
import usuarios
from analizar_partida import modelo, columnas
from campeon import datos
from capa1 import DIMENSIONES

ctk.set_widget_scaling(1.0)
ctk.set_window_scaling(1.0)

# COLORES
BLANCO = "#FCFCFD"
MORADO = "#550469"
MORADO_CLARO = "#8B5696"
NEGRO = "#101010"
NARANJA = "#F5A800"
TEXTO = "#4E4E4E"
GRIS = "#666666"

# FONTS
BODY = ("League Spartan", 16)
BODYBOLD = ("League Spartan", 16, "bold")
SMALLBODY = ("League Spartan", 12)
TITLE = ("League Spartan", 58, "bold")
SUBTITLE = ("League Spartan", 21, "bold")

# MEDIDAS
BANNER = (1170, 345)
FOOTER = (1170, 355)
FOTO = (272, 324)
PIEZAS = (115, 115)
CARD = (244, 220)
MINI = (90, 90)
CORONA = (33, 33)

AQUI = os.path.dirname(os.path.abspath(__file__))
CARPETA = os.path.join(AQUI, "imagenes")


def abrir(nombre, tam, relleno="#D9A8EE"):
    ruta = os.path.join(CARPETA, nombre)
    if os.path.exists(ruta):
        return Image.open(ruta).convert("RGBA").resize(tam, Image.LANCZOS)
    return Image.new("RGBA", tam, relleno)


def tablero_img():
    return ImageTk.PhotoImage(abrir("tablero.png", MINI))


def foto_hero(campeon, tam=FOTO):
    propia = os.path.join(CARPETA, f"{campeon.lower()}.png")
    if os.path.exists(propia):
        im = ImageOps.fit(Image.open(propia).convert("RGBA"), tam, Image.LANCZOS)
        mascara = Image.new("L", tam, 0)
        ImageDraw.Draw(mascara).rounded_rectangle((0, 0, tam[0], tam[1]), 30, fill=255)
        im.putalpha(mascara)
    else:
        im = abrir("foto.png", tam, (0, 0, 0, 0))
    return ImageTk.PhotoImage(im)


def para_ctk(nombre, tam, relleno="#D9A8EE"):
    im = abrir(nombre, (tam[0] * 2, tam[1] * 2), relleno)
    return ctk.CTkImage(light_image=im, dark_image=im, size=tam)


def partidas_similares(campeon, x, n=3):
    d = pd.read_csv(os.path.join(AQUI, "base_entrenamiento.csv")).drop_duplicates()
    d = d[d["campeon"] == campeon].copy()
    X = (d[columnas].values - np.array(modelo["media"])) / np.array(modelo["escala"])
    d["dist"] = np.linalg.norm(X - x, axis=1)
    return d.sort_values("dist").drop_duplicates("partida").head(n)["partida"].tolist()


def texto_explicacion(campeon, estilo, n):
    top = sorted(estilo, key=estilo.get, reverse=True)[:3]
    nombres = [t.replace("_", " ") for t in top]
    base = "tu partida" if n == 1 else f"tus {n} partidas"
    return (f"Analizando {base}, tus dimensiones más marcadas fueron {nombres[0]}, "
            f"{nombres[1]} y {nombres[2]}. Esa combinación se parece al juego de "
            f"{datos[campeon]['nombre']}, cuyo estilo se describe como "
            f"{datos[campeon]['estilo'].lower()}.")


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
    color = {"FIABLE": "#269B63", "FIABILIDAD MEDIA": "#D99A00",
             "POCO FIABLE": "#C94B55"}.get(etiqueta, "#777777")
    panel = ctk.CTkFrame(padre, fg_color="transparent", corner_radius=0)
    panel.pack(fill="x", padx=191, pady=15)
    ctk.CTkLabel(panel, text="Fiabilidad del análisis", font=BODYBOLD,
                 text_color=NEGRO).pack(anchor="w", padx=25, pady=(20, 5))
    fila = ctk.CTkFrame(panel, fg_color="transparent")
    fila.pack(fill="x", padx=25)
    ctk.CTkLabel(fila, text=f"{acierto * 100:.1f}%", font=("League Spartan", 38, "bold"),
                 text_color=color).pack(side="left")
    ctk.CTkLabel(fila, text=etiqueta, font=BODYBOLD, text_color=color).pack(side="left", padx=15)
    progreso = ctk.CTkProgressBar(panel, height=13, progress_color=color,
                                  fg_color="#E9CFF5", corner_radius=10)
    progreso.set(acierto)
    progreso.pack(fill="x", padx=25, pady=(10, 8))
    ctk.CTkLabel(panel, text=f"Evaluación basada en {partidas} partida(s).",
                 font=SMALLBODY, text_color=GRIS).pack(anchor="w", padx=25, pady=(0, 20))


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
        cv.create_text(w / 2, 26, text=f"Partida {numero}", fill=NEGRO, font=BODYBOLD)
        cv.create_image(w / 2, 108, image=mini)
        cv.create_text(w / 2, 184, text=texto, fill=TEXTO, width=w - 35,
                       font=SMALLBODY, justify="center")

    cv.bind("<Configure>", redibujar)


def lienzo_imagen(padre, nombre, base, relleno, extra=None):
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
        cv.imagenes = [fondo]
        cv.create_image(0, 0, anchor="nw", image=fondo)
        if extra:
            extra(cv, esc, w)

    cv.bind("<Configure>", redibujar)
    return cv


# PANTALLA DE RESULTADOS (se dibuja dentro de `contenedor`)
def mostrar_resultados(contenedor, usuario, volver, reintentar):
    
    barra_sup = ctk.CTkFrame(contenedor, fg_color=BLANCO, height=48, corner_radius=0)
    barra_sup.pack(fill="x")
    ctk.CTkLabel(barra_sup, image=para_ctk("logo.png", CORONA, (0, 0, 0, 0)), text="").pack(
        side="left", padx=(40, 8), pady=8)
    ctk.CTkLabel(barra_sup, text=f"Kingship Resultados · {usuario}", font=("League Spartan", 18, "bold"),
                 text_color=MORADO).pack(side="left")
    ctk.CTkButton(barra_sup, text="← Menú", font=BODY, fg_color=BLANCO, text_color=MORADO,
                  hover_color="#EABDF2", border_color=MORADO, border_width=2, corner_radius=16,
                  width=110, height=32, command=volver).pack(side="right", padx=40)

    pagina = ctk.CTkScrollableFrame(contenedor, fg_color=BLANCO, corner_radius=0)
    pagina.pack(fill="both", expand=True)

    # CSV al día con TODAS las partidas guardadas del usuario y análisis conjunto
    ruta_csv = usuarios.generar_csv(usuario)
    r = analizar_jugador.analizar_archivo(ruta_csv)

    if r is None:
        ctk.CTkLabel(pagina, text="Todavía no hay partidas analizables.\n"
                     "Juega y guarda partidas de al menos 10 jugadas tuyas.",
                     text_color=TEXTO, font=BODY, justify="center").pack(pady=60)
        ctk.CTkButton(pagina, text="Jugar →", fg_color=NARANJA, text_color="black",
                      hover_color="#D99700", command=reintentar).pack()
        return

    n = r["partidas"]
    resultado = {c: float(p) * 100 for c, p in zip(r["campeones"], r["probabilidades"])}
    estilo = {nom: float(v) * 100 for nom, v in zip(DIMENSIONES.keys(), r["perfil"])}
    campeon = max(resultado, key=resultado.get)
    c = datos[campeon]

    # banner
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

    # descripción
    ctk.CTkLabel(pagina, text=f"Tu estilo de juego es similar a: {c['nombre']} ({resultado[campeon]:.0f}%)",
                 font=SUBTITLE, text_color=MORADO).pack(pady=(85, 21))
    ctk.CTkFrame(pagina, fg_color="#D9A8EE", height=1, width=718).pack(padx=191, anchor="w")
    ctk.CTkLabel(pagina, text=texto_explicacion(campeon, estilo, n), wraplength=718, justify="left",
                 text_color=TEXTO, font=BODY).pack(pady=21, padx=191, anchor="w")

    mostrar_fiabilidad(pagina, r["etiqueta"], r["acierto"], n)

    # top 3 partidas (según el estilo promedio de todas tus partidas)
    ctk.CTkLabel(pagina, text="Top 3 partidas recomendadas", font=BODYBOLD,
                 text_color=NEGRO).pack(anchor="w", padx=191, pady=(21, 10))
    ctk.CTkLabel(pagina, text="Utiliza estas partidas como referencia para estudiar nuevas jugadas, "
                 "descubrir estrategias y mejorar tu toma de decisiones en el tablero.",
                 wraplength=718, justify="left", font=BODY, text_color=TEXTO).pack(anchor="w", padx=191, pady=(0, 21))
    fila = ctk.CTkFrame(pagina, fg_color=BLANCO)
    fila.pack(fill="x", padx=191)
    for i, p in enumerate(partidas_similares(campeon, r["x"]), 1):
        tarjeta_partida(fila, i, p)

    # volver a jugar
    bloque = ctk.CTkFrame(pagina, fg_color=BLANCO)
    bloque.pack(pady=(51, 10), padx=191)
    ctk.CTkLabel(bloque, image=para_ctk("twoPieces.png", PIEZAS, (0, 0, 0, 0)), text="").pack(side="left")
    txt = ctk.CTkFrame(bloque, fg_color=BLANCO)
    txt.pack(side="left")
    ctk.CTkLabel(txt, text="¿Quieres intentar otra partida?", font=BODYBOLD,
                 text_color=NEGRO).pack(anchor="w", padx=21)
    ctk.CTkLabel(txt, text="Cada partida que guardes mejora la fiabilidad de tu análisis.", font=BODY,
                 text_color=GRIS, wraplength=583, justify="left").pack(anchor="w", pady=6, padx=21)
    ctk.CTkButton(txt, text="Volver a intentar →", font=BODY, fg_color=NARANJA, text_color=NEGRO,
                  hover_color="#D99700", corner_radius=20, width=170, height=36,
                  command=reintentar).pack(anchor="w", padx=21)

    # detalle de la red
    ctk.CTkLabel(pagina, text="Procesos y cálculo de red neuronal", font=BODYBOLD,
                 text_color=NEGRO).pack(anchor="w", padx=191, pady=(20, 8))
    caja = ctk.CTkFrame(pagina, fg_color="transparent", corner_radius=0, border_width=0)
    caja.pack(fill="x", padx=191, pady=(0, 30))
    ctk.CTkLabel(caja, text="Parecido con cada campeón", font=BODYBOLD,
                 text_color=MORADO).pack(pady=(14, 4), padx=30, anchor="w")
    for nombre, v in sorted(resultado.items(), key=lambda kv: -kv[1]):
        barra(caja, nombre, v)
    ctk.CTkLabel(caja, text="Tus 10 nodos de estilo", font=BODYBOLD,
                 text_color=MORADO).pack(pady=(14, 4), padx=30, anchor="w")
    for nombre, v in estilo.items():
        barra(caja, nombre.replace("_", " "), v, MORADO_CLARO)
    ctk.CTkLabel(caja, text="", height=8).pack()

    lienzo_imagen(pagina, "footer.png", FOOTER, "#55076B")