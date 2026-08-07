# esta é uma versão PT-BR do código, com traduções e ajustes para o idioma português. 
# As funções de classificação foram adaptadas para refletir os termos corretos em português, como "Piloto", "Equipe" e "Pontos". 
# Além disso, a interface do usuário foi ajustada para exibir corretamente os títulos e rótulos em português.

import os
import pandas as pd

from shiny import App, ui, render
from modules.resultados_home import resultados_home_ui, resultados_home_server
from modules.resultados_2026 import resultados_2026_ui, resultados_2026_server

os.environ["NO_PROXY"] = "localhost,127.0.0.1,::1"

# Carrega corridas principais
caminho_race = os.path.join(os.path.dirname(__file__), "data", "Formula1_2026Season_RaceResults.csv")
df_race = pd.read_csv(caminho_race)

# Carrega corridas sprint
caminho_sprint = os.path.join(os.path.dirname(__file__), "data", "Formula1_2026Season_SprintResults.csv")
df_sprint = pd.read_csv(caminho_sprint)

# Normaliza nomes de equipes inconsistentes no dataset
NORMALIZACAO_EQUIPES = {
    "Racing Bulls": "Racing Bulls Red Bull Ford",
    "Alpine Renault": "Alpine Mercedes",
}
df_race['Team'] = df_race['Team'].replace(NORMALIZACAO_EQUIPES)
df_sprint['Team'] = df_sprint['Team'].replace(NORMALIZACAO_EQUIPES)

# Combina para classificação (corridas + sprints)
df_classificacao = pd.concat([df_race, df_sprint], ignore_index=True)

# Para resultados por GP, apenas corridas principais
df_resultados = df_race

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_radio_buttons(
            "navegacao",
            label="",
            choices={
                "home": "Início",
                "resultados_2026": "Corridas 2026"
            },
            selected="home"
        ),
        bg="#1f1f2b",
        fg="#ffffff",
    ),
    ui.include_css("www/styles.css"),
    ui.output_ui("conteudo_pagina")
)

def server(input, output, session):
    tracks = sorted(df_resultados['Track'].unique().tolist())
    
    @render.ui
    def conteudo_pagina():
        if input.navegacao() == "home":
            return resultados_home_ui("home")
        elif input.navegacao() == "resultados_2026":
            return resultados_2026_ui("resultados_2026", tracks)
        return ui.p("Página não encontrada")

    resultados_home_server("home", df_classificacao)         # ← corridas + sprints
    resultados_2026_server("resultados_2026", df_resultados)  # ← só corridas

app = App(app_ui, server, static_assets=os.path.join(os.path.dirname(__file__), "www"))