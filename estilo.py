import customtkinter as ctk

from campeon import datos

FONDO = "#282828"
TARJETA = "#2E1A33"
MORADO = "#8B5696"
MORADO_BOTON = "#7B3FD6"
CREMA = "#EEEED2"
COLOR_FIABILIDAD = {"POCO FIABLE": "#C0392B", "FIABILIDAD MEDIA": "#D68910", "FIABLE": "#2E8B57"}


def _barra(padre, texto, valor):
    # valor de 0 a 100
    fila = ctk.CTkFrame(padre, fg_color="transparent")
    fila.pack(fill="x", padx=18, pady=2)
    ctk.CTkLabel(fila, text=texto, width=120, anchor="w", font=("Segoe UI", 13), text_color=CREMA).pack(side="left")
    barra = ctk.CTkProgressBar(fila, width=170, height=12, fg_color=FONDO, progress_color=MORADO_BOTON)
    barra.set(valor / 100)
    barra.pack(side="left", padx=6)
    ctk.CTkLabel(fila, text=f"{valor:.0f} %", width=44, anchor="e", font=("Segoe UI", 13), text_color=CREMA).pack(side="left")


def _volver(contenedor, volver):
    ctk.CTkButton(contenedor, text="← Volver", font=("Segoe UI", 17, "bold"), fg_color=MORADO_BOTON,
                  hover_color=MORADO, corner_radius=14, width=180, height=46, command=volver).pack(pady=18)


def mostrar_estilo(contenedor, usuario, volver):
    from analizar_partida import analizar_usuario   # carga la red solo al abrir esta pantalla

    r = analizar_usuario(usuario)
    ctk.CTkLabel(contenedor, text=f"Estilo de {usuario}", font=("Georgia", 34, "bold"),
                 text_color=CREMA).pack(pady=(22, 4))
    if r is None:
        ctk.CTkLabel(contenedor, text="Todavía no hay partidas que analizar.\nJuega y guarda partidas de al menos 10 jugadas tuyas.",
                     font=("Segoe UI", 17), text_color="gray", justify="center").pack(pady=60)
        _volver(contenedor, volver)
        return

    nombre, pct = r["campeones"][0]
    ctk.CTkLabel(contenedor, text=f'{datos[nombre]["pieza"]}  Te pareces a {nombre}  ({pct:.0f} %)',
                 font=("Segoe UI", 28, "bold"), text_color=CREMA).pack(pady=(4, 8))
    ctk.CTkLabel(contenedor, text=r["fiabilidad"], font=("Segoe UI", 14, "bold"), text_color="white",
                 fg_color=COLOR_FIABILIDAD[r["fiabilidad"]], corner_radius=16, width=190, height=32).pack()
    info = f'{r["n"]} partida(s) analizadas · con {r["k"]} partida(s) la red acertó el {r["acierto"] * 100:.0f} % en las pruebas'
    if r["siguiente"]:
        info += f'\nCon {r["siguiente"][0]} partidas la fiabilidad sube a {r["siguiente"][1] * 100:.0f} %: ¡sigue jugando!'
    ctk.CTkLabel(contenedor, text=info, font=("Segoe UI", 14), text_color="gray", justify="center").pack(pady=(8, 12))

    columnas = ctk.CTkFrame(contenedor, fg_color=FONDO)
    columnas.pack()
    for titulo, filas in (("Parecido con cada campeón", r["campeones"]),
                          ("Tu perfil de estilo", [(k.replace("_", " ").capitalize(), v) for k, v in r["perfil"].items()])):
        tarjeta = ctk.CTkFrame(columnas, fg_color=TARJETA, border_color=MORADO, border_width=2, corner_radius=20)
        tarjeta.pack(side="left", padx=10, anchor="n")
        ctk.CTkLabel(tarjeta, text=titulo, font=("Segoe UI", 16, "bold"), text_color=CREMA).pack(pady=(12, 6))
        for texto, valor in filas:
            _barra(tarjeta, texto, valor)
        ctk.CTkLabel(tarjeta, text="", height=6).pack()
    _volver(contenedor, volver)
