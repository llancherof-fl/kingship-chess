import os

import customtkinter as ctk
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageOps

import analizar_jugador
import usuarios
from analizar_partida import modelo, columnas
from campeon import datos
from capa1 import DIMENSIONES

ctk.set_widget_scaling(1.0)
ctk.set_window_scaling(1.0)

# COLORES (LOS MISMOS DEL INICIO Y EL TABLERO)
FONDO = "#282828"
TARJETA = "#2E1A33"
TARJETA_HOVER = "#45264D"
MORADO = "#8B5696"
MORADO_BOTON = "#7B3FD6"
LILA = "#B98CC4"
CREMA = "#EEEED2"
GRIS = "gray"
BARRA_FONDO = "#3A3A3A"

# LETRAS (LAS MISMAS DEL INICIO)
TITULO = ("Georgia", 40, "bold")
SUBTITULO = ("Georgia", 22, "bold")
CUERPO = ("Segoe UI", 15)
CUERPO_BOLD = ("Segoe UI", 15, "bold")
PEQUENA = ("Segoe UI", 13)

# NOMBRES BONITOS DE LOS NODOS
NOMBRES = {
    "actividad": "Actividad",
    "desarrollo": "Desarrollo",
    "posicion_armonica": "Posición armónica",
    "agresividad": "Agresividad",
    "tactica": "Táctica",
    "estrategia": "Estrategia",
    "apertura": "Apertura",
    "defensa": "Defensa",
    "casillas_debiles": "Casillas débiles",
    "tecnica_medio": "Técnica en el medio juego",
}

# MEDIDAS
FOTO = (230, 274)
MINI = (90, 90)
PIEZAS = (90, 90)
LOGO = (30, 30)
MARGEN = 110

AQUI = os.path.dirname(os.path.abspath(__file__))
CARPETA = os.path.join(AQUI, "imagenes")


# IMAGENES
def abrir(nombre, tam, relleno=TARJETA):
    ruta = os.path.join(CARPETA, nombre)
    if os.path.exists(ruta):
        return Image.open(ruta).convert("RGBA").resize(tam, Image.LANCZOS)
    return Image.new("RGBA", tam, relleno)


def para_ctk(nombre, tam, relleno=(0, 0, 0, 0)):
    im = abrir(nombre, (tam[0] * 2, tam[1] * 2), relleno)
    return ctk.CTkImage(light_image=im, dark_image=im, size=tam)


def foto_campeon(campeon, tam=FOTO):
    ruta = os.path.join(CARPETA, f"{campeon.lower()}.png")
    if os.path.exists(ruta):
        im = ImageOps.fit(Image.open(ruta).convert("RGBA"), (tam[0] * 2, tam[1] * 2), Image.LANCZOS)
    else:
        im = Image.new("RGBA", (tam[0] * 2, tam[1] * 2), MORADO)
    mascara = Image.new("L", im.size, 0)
    ImageDraw.Draw(mascara).rounded_rectangle((0, 0, im.size[0], im.size[1]), 40, fill=255)
    im.putalpha(mascara)
    return ctk.CTkImage(light_image=im, dark_image=im, size=tam)


def coma(valor, decimales=1):
    return f"{valor:.{decimales}f}".replace(".", ",")


# PARTIDAS PARECIDAS (VECINOS MAS CERCANOS)
def partidas_similares(campeon, x, n=3):
    d = pd.read_csv(os.path.join(AQUI, "base_entrenamiento.csv")).drop_duplicates()
    d = d[d["campeon"] == campeon].copy()
    X = (d[columnas].values - np.array(modelo["media"])) / np.array(modelo["escala"])
    d["dist"] = np.linalg.norm(X - x, axis=1)
    return d.sort_values("dist").drop_duplicates("partida").head(n)["partida"].tolist()


def texto_explicacion(campeon, estilo, n):
    top = sorted(estilo, key=estilo.get, reverse=True)[:3]
    nombres = [NOMBRES.get(t, t).lower() for t in top]
    base = "tu partida" if n == 1 else f"tus {n} partidas"
    return (f"Analizando {base}, tus dimensiones más marcadas fueron {nombres[0]}, "
            f"{nombres[1]} y {nombres[2]}. Esa combinación se parece al juego de "
            f"{datos[campeon]['nombre']}, cuyo estilo se describe como "
            f"{datos[campeon]['estilo'].lower()}.")


# PIEZAS DE LA PAGINA
def caja(padre, **extra):
    marco = ctk.CTkFrame(padre, fg_color=TARJETA, border_color=MORADO, border_width=2,
                         corner_radius=20, **extra)
    return marco


def titulo_seccion(padre, texto):
    ctk.CTkLabel(padre, text=texto, font=SUBTITULO, text_color=CREMA).pack(
        anchor="w", padx=MARGEN, pady=(34, 12))


def barra(padre, texto, valor, color=MORADO_BOTON):
    fila = ctk.CTkFrame(padre, fg_color="transparent")
    fila.pack(fill="x", padx=28, pady=4)
    ctk.CTkLabel(fila, text=texto, width=210, anchor="w", text_color=CREMA,
                 font=CUERPO).pack(side="left")
    b = ctk.CTkProgressBar(fila, progress_color=color, fg_color=BARRA_FONDO, height=12,
                           corner_radius=6)
    b.set(valor / 100)
    b.pack(side="left", fill="x", expand=True, padx=12)
    ctk.CTkLabel(fila, text=f"{valor:.0f} %", width=55, anchor="e", text_color=LILA,
                 font=CUERPO_BOLD).pack(side="left")


def mostrar_fiabilidad(padre, etiqueta, acierto, partidas):
    color = {"FIABLE": "#4CAF7A", "FIABILIDAD MEDIA": "#E0B23C",
             "POCO FIABLE": "#E5534B"}.get(etiqueta, GRIS)
    panel = caja(padre)
    panel.pack(fill="x", padx=MARGEN)
    fila = ctk.CTkFrame(panel, fg_color="transparent")
    fila.pack(fill="x", padx=28, pady=(22, 4))
    ctk.CTkLabel(fila, text=f"{coma(acierto * 100)} %", font=("Georgia", 40, "bold"),
                 text_color=color).pack(side="left")
    ctk.CTkLabel(fila, text=etiqueta, font=("Segoe UI", 15, "bold"), text_color="white",
                 fg_color=color, corner_radius=14, height=30).pack(side="left", padx=18, ipadx=10)
    progreso = ctk.CTkProgressBar(panel, height=14, progress_color=color,
                                  fg_color=BARRA_FONDO, corner_radius=7)
    progreso.set(acierto)
    progreso.pack(fill="x", padx=28, pady=(10, 8))
    texto = "1 partida" if partidas == 1 else f"{partidas} partidas"
    ctk.CTkLabel(panel, text=f"Evaluación basada en {texto}. Entre más partidas juegues, más confiable es el resultado.",
                 font=PEQUENA, text_color=GRIS, wraplength=700, justify="left").pack(
        anchor="w", padx=28, pady=(0, 20))


def tarjeta_partida(padre, numero, texto, mini):
    tarjeta = caja(padre)
    tarjeta.pack(side="left", fill="both", expand=True, padx=8)
    ctk.CTkLabel(tarjeta, text=f"Partida {numero}", font=CUERPO_BOLD,
                 text_color=CREMA).pack(pady=(18, 8))
    ctk.CTkLabel(tarjeta, image=mini, text="").pack()
    ctk.CTkLabel(tarjeta, text=texto, font=PEQUENA, text_color=LILA, wraplength=200,
                 justify="center").pack(padx=14, pady=(10, 18))


# PANTALLA DE RESULTADOS (SE DIBUJA DENTRO DE LA MISMA VENTANA)
def mostrar_resultados(contenedor, usuario, volver, reintentar):

    # barra de arriba
    barra_sup = ctk.CTkFrame(contenedor, fg_color=FONDO, height=56, corner_radius=0)
    barra_sup.pack(fill="x")
    ctk.CTkLabel(barra_sup, text="♚", font=("Segoe UI Symbol", 26), text_color=CREMA).pack(
        side="left", padx=(40, 8), pady=8)
    ctk.CTkLabel(barra_sup, text="KINGSHIP", font=("Georgia", 22, "bold"),
                 text_color=CREMA).pack(side="left")
    ctk.CTkLabel(barra_sup, text=f"  ·  Resultados de {usuario}", font=CUERPO,
                 text_color=GRIS).pack(side="left")
    ctk.CTkButton(barra_sup, text="← Inicio", font=("Segoe UI", 14, "bold"), fg_color=FONDO,
                  hover_color=TARJETA, border_color=MORADO_BOTON, border_width=2, corner_radius=12,
                  text_color=CREMA, width=110, height=34, command=volver).pack(side="right", padx=40)

    pagina = ctk.CTkScrollableFrame(contenedor, fg_color=FONDO, corner_radius=0,
                                    scrollbar_button_color=MORADO,
                                    scrollbar_button_hover_color=MORADO_BOTON)
    pagina.pack(fill="both", expand=True)

    # CSV al día con TODAS las partidas guardadas del usuario y análisis conjunto
    ruta_csv = usuarios.generar_csv(usuario)
    r = analizar_jugador.analizar_archivo(ruta_csv)

    if r is None:
        aviso = caja(pagina)
        aviso.pack(padx=MARGEN, pady=80, fill="x")
        ctk.CTkLabel(aviso, text="♟", font=("Segoe UI Symbol", 56), text_color=CREMA).pack(pady=(26, 0))
        ctk.CTkLabel(aviso, text="Todavía no hay partidas analizables", font=SUBTITULO,
                     text_color=CREMA).pack(pady=(4, 6))
        ctk.CTkLabel(aviso, text="Juega y guarda partidas de al menos 10 jugadas tuyas.",
                     font=CUERPO, text_color=GRIS).pack()
        ctk.CTkButton(aviso, text="Jugar", font=("Segoe UI", 18, "bold"), fg_color=MORADO_BOTON,
                      hover_color=MORADO, corner_radius=14, width=200, height=48,
                      command=reintentar).pack(pady=(18, 28))
        return

    n = r["partidas"]
    resultado = {c: float(p) * 100 for c, p in zip(r["campeones"], r["probabilidades"])}
    estilo = {nom: float(v) * 100 for nom, v in zip(DIMENSIONES.keys(), r["perfil"])}
    campeon = max(resultado, key=resultado.get)
    c = datos[campeon]

    # campeon principal
    principal = caja(pagina)
    principal.pack(fill="x", padx=MARGEN, pady=(30, 0))
    texto = ctk.CTkFrame(principal, fg_color="transparent")
    texto.pack(side="left", fill="both", expand=True, padx=(34, 10), pady=28)
    ctk.CTkLabel(texto, text="TU ESTILO SE PARECE A", font=("Segoe UI", 13, "bold"),
                 text_color=LILA).pack(anchor="w")
    ctk.CTkLabel(texto, text=f"{c['pieza']}  {c['nombre']}", font=TITULO, text_color=CREMA,
                 wraplength=520, justify="left").pack(anchor="w", pady=(4, 2))
    ctk.CTkLabel(texto, text=c["titulo"], font=CUERPO, text_color=GRIS).pack(anchor="w")
    chips = ctk.CTkFrame(texto, fg_color="transparent")
    chips.pack(anchor="w", pady=(16, 14))
    ctk.CTkLabel(chips, text="Estilo: " + c["estilo"], font=("Segoe UI", 15, "bold"),
                 fg_color=MORADO, text_color="white", corner_radius=16, height=34).pack(
        side="left", ipadx=14)
    ctk.CTkLabel(chips, text=f"{resultado[campeon]:.0f} % de parecido", font=("Segoe UI", 15, "bold"),
                 fg_color=MORADO_BOTON, text_color="white", corner_radius=16, height=34).pack(
        side="left", padx=10, ipadx=14)
    ctk.CTkLabel(texto, text=texto_explicacion(campeon, estilo, n), wraplength=520, justify="left",
                 text_color=CREMA, font=CUERPO).pack(anchor="w")
    ctk.CTkLabel(principal, image=foto_campeon(campeon), text="").pack(side="right", padx=28, pady=24)

    # fiabilidad
    titulo_seccion(pagina, "Fiabilidad del análisis")
    mostrar_fiabilidad(pagina, r["etiqueta"], r["acierto"], n)

    # parecido con cada campeon y nodos
    titulo_seccion(pagina, "Parecido con cada campeón")
    caja_campeones = caja(pagina)
    caja_campeones.pack(fill="x", padx=MARGEN)
    ctk.CTkLabel(caja_campeones, text="", height=6).pack()
    for nombre, v in sorted(resultado.items(), key=lambda kv: -kv[1]):
        barra(caja_campeones, f"{datos[nombre]['pieza']}  {nombre}", v)
    ctk.CTkLabel(caja_campeones, text="", height=6).pack()

    titulo_seccion(pagina, "Tus 10 nodos de estilo")
    caja_nodos = caja(pagina)
    caja_nodos.pack(fill="x", padx=MARGEN)
    ctk.CTkLabel(caja_nodos, text="", height=6).pack()
    for nombre, v in estilo.items():
        barra(caja_nodos, NOMBRES.get(nombre, nombre), v, MORADO)
    ctk.CTkLabel(caja_nodos, text="", height=6).pack()

    # top 3 partidas (según el estilo promedio de todas tus partidas)
    titulo_seccion(pagina, "Partidas recomendadas para estudiar")
    ctk.CTkLabel(pagina, text=f"Las tres partidas de {c['nombre']} que más se parecen a tu forma de jugar.",
                 font=CUERPO, text_color=GRIS).pack(anchor="w", padx=MARGEN, pady=(0, 12))
    fila = ctk.CTkFrame(pagina, fg_color="transparent")
    fila.pack(fill="x", padx=MARGEN - 8)
    mini = para_ctk("tablero.png", MINI, MORADO)
    for i, p in enumerate(partidas_similares(campeon, r["x"]), 1):
        tarjeta_partida(fila, i, p, mini)

    # volver a jugar
    bloque = caja(pagina)
    bloque.pack(fill="x", padx=MARGEN, pady=(34, 40))
    ctk.CTkLabel(bloque, image=para_ctk("twoPieces.png", PIEZAS), text="").pack(
        side="left", padx=(28, 10), pady=20)
    txt = ctk.CTkFrame(bloque, fg_color="transparent")
    txt.pack(side="left", fill="x", expand=True, pady=20)
    ctk.CTkLabel(txt, text="¿Quieres intentar otra partida?", font=SUBTITULO,
                 text_color=CREMA).pack(anchor="w")
    ctk.CTkLabel(txt, text="Cada partida que guardes mejora la fiabilidad de tu análisis.",
                 font=CUERPO, text_color=GRIS).pack(anchor="w", pady=(4, 0))
    ctk.CTkButton(bloque, text="Jugar otra", font=("Segoe UI", 18, "bold"), fg_color=MORADO_BOTON,
                  hover_color=MORADO, corner_radius=14, width=180, height=50,
                  command=reintentar).pack(side="right", padx=28)