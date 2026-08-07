"""
Utilitário compartilhado para logos de times nas tabelas.
Importe de qualquer módulo: from utils.team_logos import TEAM_LOGO_MAP, LOGO_DIR, build_team_styles
"""

TEAM_LOGO_MAP = {
    "Ferrari":                      "team_ferrari-normalized-logo.avif",
    "Mercedes":                     "team_2026-mercedes-normalized-logo.avif",
    "McLaren Mercedes":             "team_mclaren-normalized-logo.avif",
    "Red Bull Racing Red Bull Ford":"team_rbr-normalized-logo.avif",
    "Haas Ferrari":                 "team_haas-normalized-logo.avif",
    "Racing Bulls Red Bull Ford":   "team_rb-normalized-logo.avif",
    "Audi":                         "team_audi-normalized-logo.avif",
    "Alpine Mercedes":              "team_alpine-normalized-logo.avif",
    "Williams Mercedes":            "team_2026-williams-normalized-logo.avif",
    "Cadillac Ferrari":             "team_cadillac-normalized-logo.avif",
    "Aston Martin Honda":           "team_aston-martin-normalized-logo.avif",
}

LOGO_DIR = "Team Logos"


def build_team_styles(df, team_col_idx: int) -> list:
    """
    Constrói estilos CSS (background-image) com o logo em cada
    célula da coluna de time.
    
    Args:
        df: DataFrame com coluna 'Team' (nomes originais)
        team_col_idx: índice da coluna Team
    Returns:
        Lista de dicts no formato esperado por render.DataGrid(styles=...)
    """
    team_col = df.columns[team_col_idx]
    styles_list = []
    for row_idx, team in enumerate(df[team_col]):
        filename = TEAM_LOGO_MAP.get(team)
        if filename:
            styles_list.append({
                "rows": [row_idx],
                "cols": [team_col_idx],
                "style": {
                    "background-image": f"url('{LOGO_DIR}/{filename}')",
                    "background-size": "contain",
                    "background-repeat": "no-repeat",
                    "background-position": "center",
                    "color": "transparent",
                    "min-width": "60px",
                    "min-height": "30px",
                },
            })
    return styles_list