import csv
import re
import sys

CAMPEONES = {
    "Capablanca, Jose Raul": "Capablanca",
    "Tal, Mihail": "Tal",
    "Petrosian, Tigran V": "Petrosian",
    "Karpov, Anatoly": "Karpov",
    "Carlsen, Magnus": "Carlsen",
}
NO_CLASICAS = ("blitz", "rapid", "simul", "sim ", "bullet", "blind", "armageddon",
               "960", "exhib", "casual", "titled")
RESULTADOS = ("1-0", "0-1", "1/2-1/2", "*")

COLUMNAS = ["jugadas", "pct_capturas", "pct_jaques", "pct_peon", "pct_rey",
            "pct_dama", "pct_tranquilas", "enroque_jugada", "enroque_largo",
            "cambio_damas_temprano", "jugada_cambio_damas", "corona",
            "color_blancas", "apertura_e4", "apertura_d4", "apertura_flanco",
            "resp_simetrica", "pct_caballo", "pct_alfil", "pct_torre",
            "pct_campo_rival", "pct_peon_avanzado", "pct_peon_flanco_rey",
            "capt_apertura", "capt_medio", "capt_final", "jaq_apertura", "jaq_medio", "jaq_final",
            "jugadas_tras_40"]


def leer_partidas(ruta):
    texto = open(ruta, encoding="utf-8", errors="replace").read().replace("\r\n", "\n")
    for bloque in re.split(r"\n(?=\[Event )", texto):
        if not bloque.strip():
            continue
        cab = dict(re.findall(r'\[(\w+) "([^"]*)"\]', bloque))
        cuerpo = re.sub(r"\[[^\]]*\]", " ", bloque)
        cuerpo = re.sub(r"\{[^}]*\}", " ", cuerpo)         
        cuerpo = re.sub(r";[^\n]*", " ", cuerpo)
        while True:                                        
            nuevo = re.sub(r"\([^()]*\)", " ", cuerpo)
            if nuevo == cuerpo:
                break
            cuerpo = nuevo
        cuerpo = re.sub(r"\$\d+", " ", cuerpo)              
        cuerpo = re.sub(r"\d+\.(\.\.)?", " ", cuerpo)     
        jugadas = [j.rstrip("!?") for j in cuerpo.split() if j not in RESULTADOS]
        yield cab, [j for j in jugadas if j]


def es_clasica(cab):
    ev = (cab.get("EventType", "") + " " + cab.get("Event", "")).lower()
    return not any(z in ev for z in NO_CLASICAS)


def parametros(jugadas, color):
    mias = jugadas[color::2]
    n = len(mias)
    if n < 10:
        return None
    cuenta = lambda f: sum(1 for j in mias if f(j)) / n * 100
    enroque, largo = 0, 0
    for i, j in enumerate(mias, 1):
        if j.startswith("O-O"):
            enroque, largo = i, int(j.startswith("O-O-O"))
            break
    jug_cambio = 0
    for i in range(len(jugadas) - 1):
        m = re.match(r"^Qx([a-h][1-8])", jugadas[i])
        if m and ("x" + m.group(1)) in jugadas[i + 1]:
            jug_cambio = i // 2 + 1
            break
    def fila(j):
        m = re.findall(r"[a-h]([1-8])", j)
        if not m:
            return 0
        r = int(m[-1])
        return r if color == 0 else 9 - r
    def fase(a, b, f):
        tramo = mias[a:b]
        return sum(1 for j in tramo if f(j)) / len(tramo) * 100 if tramo else 0
    es_capt = lambda j: "x" in j
    es_jaq = lambda j: "+" in j or "#" in j
    primera = jugadas[0] if jugadas else ""
    resp = jugadas[1] if len(jugadas) > 1 else ""
    return {
        "jugadas": (len(jugadas) + 1) // 2,
        "pct_capturas": cuenta(lambda j: "x" in j),
        "pct_jaques": cuenta(lambda j: "+" in j or "#" in j),
        "pct_peon": cuenta(lambda j: j[0] in "abcdefgh"),
        "pct_rey": cuenta(lambda j: j[0] == "K"),
        "pct_dama": cuenta(lambda j: j[0] == "Q"),
        "pct_tranquilas": cuenta(lambda j: "x" not in j and "+" not in j and "#" not in j),
        "enroque_jugada": enroque,
        "enroque_largo": largo,
        "cambio_damas_temprano": int(0 < jug_cambio <= 25),
        "jugada_cambio_damas": jug_cambio,
        "corona": int(any("=" in j for j in mias)),
        "color_blancas": int(color == 0),
        "apertura_e4": int(primera == "e4"),
        "apertura_d4": int(primera == "d4"),
        "apertura_flanco": int(primera in ("c4", "Nf3", "g3", "b3", "f4", "b4")),
        "resp_simetrica": int(len(resp) == 2 and len(primera) == 2 and resp[0] == primera[0]),
        "pct_caballo": cuenta(lambda j: j[0] == "N"),
        "pct_alfil": cuenta(lambda j: j[0] == "B"),
        "pct_torre": cuenta(lambda j: j[0] == "R"),
        "pct_campo_rival": cuenta(lambda j: fila(j) >= 5),
        "pct_peon_avanzado": cuenta(lambda j: j[0] in "abcdefgh" and fila(j) >= 5),
        "pct_peon_flanco_rey": cuenta(lambda j: j[0] in "fgh" and "x" not in j),
        "capt_apertura": fase(0, 15, es_capt), "capt_medio": fase(15, 40, es_capt),
        "capt_final": fase(40, None, es_capt),
        "jaq_apertura": fase(0, 15, es_jaq), "jaq_medio": fase(15, 40, es_jaq),
        "jaq_final": fase(40, None, es_jaq),
        "jugadas_tras_40": max(0, n - 40),
    }


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    entrada, salida = sys.argv[1], sys.argv[2]
    jugador = sys.argv[sys.argv.index("--jugador") + 1] if "--jugador" in sys.argv else None
    filas = []
    for cab, jug in leer_partidas(entrada):
        if cab.get("Result") not in ("1-0", "0-1", "1/2-1/2"):
            continue
        w, b = cab.get("White"), cab.get("Black")
        if jugador:
            lados = [(0, jugador)] if w == jugador else [(1, jugador)] if b == jugador else []
        else:
            if not es_clasica(cab):
                continue
            lados = [(c, CAMPEONES[x]) for c, x in ((0, w), (1, b)) if x in CAMPEONES]
        for color, etiqueta in lados:
            p = parametros(jug, color)
            if p:
                p.update(campeon=etiqueta, partida=f"{w} - {b}, {cab.get('Event','')} {cab.get('Date','')[:4]}",
                         anio=cab.get("Date", "")[:4])
                filas.append(p)
    with open(salida, "w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=["campeon", "partida", "anio"] + COLUMNAS)
        wr.writeheader()
        wr.writerows(filas)
    print(f"{len(filas)} filas escritas en {salida}")


if __name__ == "__main__":
    main()
