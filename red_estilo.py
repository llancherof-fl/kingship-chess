
import sys

import numpy as np
import pandas as pd
import torch
import torch.nn as nn

from capa1 import DIMENSIONES, RedEstilo
from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix
from sklearn.model_selection import GroupShuffleSplit
from sklearn.preprocessing import StandardScaler

torch.manual_seed(0)
np.random.seed(0)

EPOCAS = 200
LR = 0.01
PACIENCIA = 25
VENTANAS = [1, 3, 5, 10, 20, 40] 


# -----DATOS -----------------------------------------------
ruta = sys.argv[1] if len(sys.argv) > 1 else "base_entrenamiento.csv"
d = pd.read_csv(ruta).drop_duplicates().reset_index(drop=True)

columnas = [c for c in d.columns if c not in ("campeon", "partida", "anio")]
clases = sorted(d["campeon"].unique())
y = d["campeon"].map({c: i for i, c in enumerate(clases)}).values
X = d[columnas].values.astype(np.float32)
grupos = d["partida"].values

gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
idx_tr, idx_te = next(gss.split(X, y, groups=grupos))
gss2 = GroupShuffleSplit(n_splits=1, test_size=0.15, random_state=7)
sub_tr, sub_va = next(gss2.split(X[idx_tr], y[idx_tr], groups=grupos[idx_tr]))
idx_va = idx_tr[sub_va]
idx_tr = idx_tr[sub_tr]




escalador = StandardScaler().fit(X[idx_tr])
t = lambda idx: torch.tensor(escalador.transform(X[idx]), dtype=torch.float32)
Xtr, Xva, Xte = t(idx_tr), t(idx_va), t(idx_te)
ytr = torch.tensor(y[idx_tr]); yva = torch.tensor(y[idx_va]); yte = y[idx_te]

# pesos por clase por el desbalanceo de partidas
cuentas = np.bincount(y[idx_tr], minlength=len(clases))
pesos = torch.tensor(len(idx_tr) / (len(clases) * cuentas), dtype=torch.float32)


#-------------entrenamiento --------------------------------------------------------------------------------------------
red = RedEstilo(columnas, len(clases))
opt = torch.optim.Adam(red.parameters(), lr=LR, weight_decay=1e-3)
perdida = nn.CrossEntropyLoss(weight=pesos)

mejor, mejor_estado, sin_mejora = 1e9, None, 0

for epoca in range(EPOCAS):
    red.train()
    orden = torch.randperm(len(Xtr))
    for i in range(0, len(orden), 128):
        lote = orden[i:i + 128]
        opt.zero_grad()
        perdida(red(Xtr[lote]), ytr[lote]).backward()
        opt.step()

    red.eval()
    with torch.no_grad():
        pv = perdida(red(Xva), yva).item()

    if pv < mejor - 1e-4:
        mejor, sin_mejora = pv, 0
        mejor_estado = {k: v.clone() for k, v in red.state_dict().items()}
    else:
        sin_mejora += 1
        if sin_mejora >= PACIENCIA:
            break

red.load_state_dict(mejor_estado)
red.eval()
print(f"Entrenó {epoca + 1} épocas (mejor pérdida de validación: {mejor:.3f})")

# -----salida en consola------------------------------------------------------------------------------------
with torch.no_grad():
    P = torch.softmax(red(Xte), dim=1).numpy()
pred = P.argmax(axis=1)

print("\n--- Por partida suelta ---")
print(f"Exactitud: {accuracy_score(yte, pred) * 100:.1f} %   "
      f"balanceada: {balanced_accuracy_score(yte, pred) * 100:.1f} %   "
      f"(mayoritaria: {np.bincount(yte).max() / len(yte) * 100:.1f} %)")
print(pd.DataFrame(confusion_matrix(yte, pred), index=clases, columns=clases))

print("\n--- Acierto según cuántas partidas del mismo jugador se juntan ---")
rng = np.random.default_rng(0)
fiabilidad = {}
for k in VENTANAS:
    por_clase = []
    for c in range(len(clases)):
        idx = np.where(yte == c)[0]
        ok = 0
        for _ in range(300):
            s = rng.choice(idx, size=min(k, len(idx)), replace=False)
            ok += P[s].mean(axis=0).argmax() == c
        por_clase.append(ok / 300)
    fiabilidad[k] = float(np.mean(por_clase))     
    detalle = "  ".join(f"{clases[c][:4]} {por_clase[c] * 100:3.0f}%" for c in range(len(clases)))
    print(f"  {k:>2} partida(s): {fiabilidad[k] * 100:5.1f} %    {detalle}")

# Aquí se muestran los perfiles según los 10 nodos de estilo-----------------------------------------------------
with torch.no_grad():
    perfiles = red.perfil(Xte).numpy()

tabla = pd.DataFrame(
    {clases[c]: perfiles[yte == c].mean(axis=0) for c in range(len(clases))},
    index=list(DIMENSIONES.keys()),
).round(2)
print("\n--- Perfil medio de los 10 nodos por campeón (0 a 1) ---")
print(tabla)




#-----------------------------------------------------------------------------------------
torch.save({"estado": red.state_dict(), "columnas": columnas, "clases": clases,
            "media": escalador.mean_.tolist(), "escala": escalador.scale_.tolist(),
            "fiabilidad": fiabilidad}, "red_estilo.pt")
print("\nModelo guardado en red_estilo.pt")
