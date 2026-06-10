import pandas as pd
import os
from shiny import ui, render, module


# =====================================================================
# MAPEAMENTO: nome do time no CSV → nome do arquivo de logo
# =====================================================================
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

LOGO_DIR = "Team Logos"   # ← agora existe em www/Team Logos/


def build_team_styles(df: pd.DataFrame, team_col_idx: int) -> list:
    """
    Constrói a lista de estilos para aplicar background-image com o logo
    em cada célula da coluna de time.
    
    Args:
        df: DataFrame com coluna 'Team' (nomes originais!)
        team_col_idx: índice da coluna Team (2=pilotos, 1=construtores)
    """
    styles_list = []
    for row_idx, team in enumerate(df['Team']):
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
                    "color": "transparent",        # ← esconde o texto
                    "min-width": "60px",
                    "min-height": "30px",
                },
            })
    return styles_list


def calcular_classificacao_pilotos(df: pd.DataFrame) -> pd.DataFrame:
    classificacao = df.groupby(['Driver', 'Team'])['Points'].sum().reset_index()
    classificacao = classificacao.sort_values('Points', ascending=False).reset_index(drop=True)
    classificacao.insert(0, 'Position', range(1, len(classificacao) + 1))
    # ← NÃO zera 'Team' aqui — o build_team_styles precisa dos nomes!
    return classificacao


def calcular_classificacao_construtores(df: pd.DataFrame) -> pd.DataFrame:
    classificacao = df.groupby('Team')['Points'].sum().reset_index()
    classificacao = classificacao.sort_values('Points', ascending=False).reset_index(drop=True)
    classificacao.insert(0, 'Position', range(1, len(classificacao) + 1))
    # ← NÃO zera 'Team' aqui — o build_team_styles precisa dos nomes!
    return classificacao


@module.ui
def resultados_home_ui():
    return ui.div(
        ui.layout_columns(
            ui.div(
                ui.h4("Classificação de Pilotos"),
                ui.output_data_frame("tabela_classificacao"),
            ),
            ui.div(
                ui.h4("Classificação de Construtores"),
                ui.output_data_frame("tabela_construtores"),
            ),
            col_widths=[6, 6],
        ),
        style="padding: 20px;"
    )


@module.server
def resultados_home_server(input, output, session, df):
    df_pilotos = calcular_classificacao_pilotos(df)
    df_construtores = calcular_classificacao_construtores(df)

    # 🔧 CORREÇÃO: constrói estilos ANTES de zerar a coluna
    pilotos_styles = build_team_styles(df_pilotos, team_col_idx=2)
    construtores_styles = build_team_styles(df_construtores, team_col_idx=1)

    # 🔧 SÓ AGORA zera a coluna Team (o texto fica transparente via CSS)
    df_pilotos['Team'] = ""
    df_construtores['Team'] = ""

    @render.data_frame
    def tabela_classificacao():
        return render.DataGrid(
            df_pilotos,
            styles=pilotos_styles,
            summary=False,
        )

    @render.data_frame
    def tabela_construtores():
        return render.DataGrid(
            df_construtores,
            styles=construtores_styles,
            summary=False,
        )