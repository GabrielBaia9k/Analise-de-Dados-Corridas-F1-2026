import os
import pandas as pd
from shiny import App, ui, render
from modules.resultados_home import resultados_home_ui, resultados_home_server
from modules.resultados_2026 import resultados_2026_ui, resultados_2026_server

os.environ["NO_PROXY"] = "localhost,127.0.0.1,::1"

caminho_csv = os.path.join(os.path.dirname(__file__), "data", "Formula1_2026Season_RaceResults.csv")
df_resultados = pd.read_csv(caminho_csv)

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_radio_buttons(
            "navegacao",
            label="",
            choices={
                "home": "Home",
                "resultados_2026": "Resultados 2026"
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
    # Extrai tracks UMA vez, fora do render
    tracks = sorted(df_resultados['Track'].unique().tolist())
    
    @render.ui
    def conteudo_pagina():
        if input.navegacao() == "home":
            return resultados_home_ui("home")
        elif input.navegacao() == "resultados_2026":
            return resultados_2026_ui("resultados_2026", tracks)  # ← passa tracks!
        return ui.p("Página não encontrada")

    resultados_home_server("home", df_resultados)
    resultados_2026_server("resultados_2026", df_resultados)

app = App(app_ui, server, static_assets=os.path.join(os.path.dirname(__file__), "www"))