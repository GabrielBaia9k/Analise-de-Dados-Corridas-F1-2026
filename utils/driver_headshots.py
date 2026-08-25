"""
Utilitário compartilhado para fotos dos pilotos (headshots).
Importe de qualquer módulo: from utils.driver_headshots import DRIVER_HEADSHOT_MAP, HEADSHOT_DIR, headshot_src
"""

HEADSHOT_DIR = "Driver Headshots"

DRIVER_HEADSHOT_MAP = {
    "Alexander Albon":  "ALB.png",
    "Fernando Alonso":  "ALO.png",
    "Kimi Antonelli":   "ANT.png",
    "Oliver Bearman":   "BEA.png",
    "Gabriel Bortoleto":"BOR.png",
    "Valtteri Bottas":  "BOT.png",
    "Franco Colapinto": "COL.png",
    "Pierre Gasly":     "GAS.png",
    "Isack Hadjar":     "HAD.png",
    "Lewis Hamilton":   "HAM.png",
    "Nico Hulkenberg":  "HUL.png",
    "Liam Lawson":      "LAW.png",
    "Charles Leclerc":  "LEC.png",
    "Arvid Lindblad":   "LIN.png",
    "Lando Norris":     "NOR.png",
    "Esteban Ocon":     "OCO.png",
    "Sergio Perez":     "PER.png",
    "Oscar Piastri":    "PIA.png",
    "George Russell":   "RUS.png",
    "Carlos Sainz":     "SAI.png",
    "Lance Stroll":     "STR.png",
    "Max Verstappen":   "VER.png",
}


def headshot_src(piloto: str) -> str | None:
    """Retorna o caminho da imagem do piloto ou None se não houver."""
    arquivo = DRIVER_HEADSHOT_MAP.get(piloto)
    return f'{HEADSHOT_DIR}/{arquivo}' if arquivo else None
