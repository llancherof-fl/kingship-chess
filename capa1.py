
import torch
import torch.nn as nn

DIMENSIONES = {
    "actividad":        ["pct_campo_rival", "pct_caballo", "pct_alfil", "pct_torre"],
    "desarrollo":       ["enroque_jugada", "enroque_largo", "pct_peon", "pct_caballo", "pct_alfil"],
    "posicion_armonica": ["pct_tranquilas", "pct_rey", "pct_peon"],
    "agresividad":      ["pct_jaques", "pct_dama", "pct_peon_avanzado", "pct_peon_flanco_rey"],
    "tactica":          ["pct_capturas", "capt_medio", "jaq_medio"],
    "estrategia":       ["cambio_damas_temprano", "jugada_cambio_damas", "jugadas", "pct_tranquilas"],
    "apertura":         ["apertura_e4", "apertura_d4", "apertura_flanco", "resp_simetrica",
                         "capt_apertura", "jaq_apertura", "color_blancas"],
    "defensa":          ["pct_rey", "pct_tranquilas", "jugadas_tras_40"],
    "casillas_debiles": ["pct_campo_rival", "pct_caballo", "pct_torre"],
    "tecnica_medio":    ["capt_medio", "jaq_medio", "capt_final", "jaq_final",
                         "jugadas_tras_40", "corona"],
}


class RedEstilo(nn.Module):

    def __init__(self, columnas, n_clases):
        super().__init__()
        n = len(columnas)
        mascara = torch.zeros(len(DIMENSIONES), n)
        for i, cols in enumerate(DIMENSIONES.values()):
            for c in cols:
                mascara[i, columnas.index(c)] = 1.0
        self.register_buffer("mascara", mascara)

        self.W = nn.Parameter(torch.randn(len(DIMENSIONES), n) * 0.1)
        self.b = nn.Parameter(torch.zeros(len(DIMENSIONES)))

        self.cabeza = nn.Sequential(
            nn.Linear(len(DIMENSIONES), 16),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(16, n_clases),
        )

    def perfil(self, x):
        return torch.sigmoid(x @ (self.W * self.mascara).T + self.b)

    def forward(self, x):
        return self.cabeza(self.perfil(x))
