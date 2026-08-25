"""
Utilitário compartilhado para traçados dos circuitos (SVG).
Importe de qualquer módulo: from utils.circuit_layouts import CIRCUIT_LAYOUT_MAP, LAYOUT_DIR, TOTAL_CORRIDAS, layout_src
"""

LAYOUT_DIR = "Circuit Layouts"

# Temporada 2026: 25 traçados disponíveis, calendário com 23 corridas
# (Bahrain e Saudi Arabia canceladas; Malaysia substitui Bahrain em 2-4 out).
TOTAL_CORRIDAS = 23

CALENDARIO_2026 = [
    "Australia",
    "China",
    "Japan",
    "Miami",
    "Canada",
    "Monaco",
    "Barcelona-Catalunya",
    "Austria",
    "Great Britain",
    "Belgium",
    "Hungary",
    "Netherlands",
    "Italy",
    "Madrid",
    "Azerbaijan",
    "Singapore",
    "Malaysia",
    "United States",
    "Mexico",
    "Brazil",
    "Las Vegas",
    "Qatar",
    "Abu Dhabi",
]


def proxima_corrida(track_disputadas) -> tuple[str, int] | None:
    """Retorna (nome_da_corrida, rodada) da próxima corrida do calendário.

    track_disputadas: coleção de nomes de pistas já disputadas
    (valores da coluna 'Track').
    """
    disputadas = set(track_disputadas)
    for rodada, track in enumerate(CALENDARIO_2026, start=1):
        if track not in disputadas:
            return track, rodada
    return None

CIRCUIT_LAYOUT_MAP = {
    "Australia":       "melbourne-2.svg",
    "Austria":         "spielberg-3.svg",
    "Bahrain":         "bahrain-1.svg",
    "Belgium":         "spa-francorchamps-4.svg",
    "Brazil":          "interlagos-2.svg",
    "Canada":          "montreal-6.svg",
    "China":           "shanghai-1.svg",
    "Great Britain":   "silverstone-8.svg",
    "Hungary":         "hungaroring-3.svg",
    "Italy":           "monza-7.svg",
    "Japan":           "suzuka-2.svg",
    "Madrid":          "madring-1.svg",
    "Malaysia":        "sepang-1.svg",
    "Mexico":          "mexico-city-3.svg",
    "Miami":           "miami-1.svg",
    "Monaco":          "monaco-6.svg",
    "Netherlands":     "zandvoort-5.svg",
    "Qatar":           "lusail-1.svg",
    "Saudi Arabia":    "jeddah-1.svg",
    "Singapore":       "marina-bay-4.svg",
    "United States":   "austin-1.svg",
    "Las Vegas":       "las-vegas-1.svg",
    "Abu Dhabi":       "yas-marina-2.svg",
    "Azerbaijan":      "baku-1.svg",
    "Barcelona-Catalunya": "catalunya-6.svg",
}


def layout_src(track: str) -> str | None:
    """Retorna o caminho do SVG do traçado ou None se não houver."""
    arquivo = CIRCUIT_LAYOUT_MAP.get(track)
    return f'{LAYOUT_DIR}/{arquivo}' if arquivo else None
