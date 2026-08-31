# esta é uma versão PT-BR do código, com traduções e ajustes para o idioma português. 
# As funções de classificação foram adaptadas para refletir os termos corretos em português, como "Piloto", "Equipe" e "Pontos". 
# Além disso, a interface do usuário foi ajustada para exibir corretamente os títulos e rótulos em português.

import os
import pandas as pd

from shiny import App, ui, render
from modules.resultados_home import resultados_home_ui, resultados_home_server
from modules.corridas_2026 import corridas_2026_ui, corridas_2026_server

os.environ["NO_PROXY"] = "localhost,127.0.0.1,::1"

# Carrega corridas principais
caminho_race = os.path.join(os.path.dirname(__file__), "data", "Formula1_2026Season_RaceResults.csv")
df_race = pd.read_csv(caminho_race)

# Carrega corridas sprint
caminho_sprint = os.path.join(os.path.dirname(__file__), "data", "Formula1_2026Season_SprintResults.csv")
df_sprint = pd.read_csv(caminho_sprint)

# Carrega classificações (qualifying)
caminho_qualy = os.path.join(os.path.dirname(__file__), "data", "Formula1_2026Season_QualifyingResults.csv")
df_qualy = pd.read_csv(caminho_qualy)

# Carrega classificações de sprint (sprint qualifying)
caminho_sprint_qualy = os.path.join(os.path.dirname(__file__), "data", "Formula1_2026Season_SprintQualifyingResults.csv")
df_sprint_qualy = pd.read_csv(caminho_sprint_qualy)

# Carrega a tabela de classificacao gerada
caminho_tabela_classificacao = os.path.join(
    os.path.dirname(__file__),
    "data",
    "Dados Gerados",
    "tabela_de_classificacao.csv",
)
df_tabela_classificacao = pd.read_csv(caminho_tabela_classificacao)

# Normaliza nomes de equipes inconsistentes no dataset
NORMALIZACAO_EQUIPES = {
    "Racing Bulls": "Racing Bulls Red Bull Ford",
    "Alpine Renault": "Alpine Mercedes",
    "Astom Martin Honda": "Aston Martin Honda",
    "Hass Ferrari": "Haas Ferrari",
}
df_race['Team'] = df_race['Team'].replace(NORMALIZACAO_EQUIPES)
df_sprint['Team'] = df_sprint['Team'].replace(NORMALIZACAO_EQUIPES)
df_qualy['Team'] = df_qualy['Team'].replace(NORMALIZACAO_EQUIPES)
df_sprint_qualy['Team'] = df_sprint_qualy['Team'].replace(NORMALIZACAO_EQUIPES)

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
                "home": "Classificação",
                "corridas_2026": "Corridas",
                "Pilotos": "Pilotos",
                "Equipes": "Equipes",
                "Sobre": "Sobre"
            },
            selected="home"
        ),
        bg="#1f1f2b",
        fg="#ffffff",
    ),
    ui.include_css("www/styles.css"),
    ui.include_js("www/hover_logos.js"),
    ui.output_ui("conteudo_pagina")
)

def server(input, output, session):
    tracks = sorted(df_resultados['Track'].unique().tolist())
    
    @render.ui
    def conteudo_pagina():
        if input.navegacao() == "home":
            return resultados_home_ui("home")
        elif input.navegacao() == "corridas_2026":
            return corridas_2026_ui("corridas_2026", tracks)
        return ui.p("Página não encontrada")

    resultados_home_server(
        "home",
        df_classificacao,
        df_tabela_classificacao,
        df_race,
        df_sprint,
        df_qualy,
        df_sprint_qualy,
    )
    corridas_2026_server("corridas_2026", df_resultados)  # ← só corridas

app = App(app_ui, server, static_assets=os.path.join(os.path.dirname(__file__), "www"))
